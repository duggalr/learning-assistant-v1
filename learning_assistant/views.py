from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.http import JsonResponse
from django import forms
from django.template.loader import render_to_string
from django.contrib.auth.hashers import make_password, check_password
from django.forms.models import model_to_dict
from django.contrib.sites.shortcuts import get_current_site
from django.conf import settings
from urllib.parse import quote_plus, urlencode

import os
import time
import functools
import secrets
import string
import datetime
from dotenv import load_dotenv, find_dotenv
from operator import itemgetter
from authlib.integrations.django_client import OAuth

from .models import *
from . import main_utils

from learning_assistant.tasks import send_student_account_create_email




if 'PRODUCTION' not in os.environ:
    dot_env_file = find_dotenv()
    load_dotenv(dot_env_file)



def user_authentication_required(view_func, redirect_url="login"):
    """
    decorator ensures that a user is logged in
    """
    @functools.wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if request.session.get("user", None) is None:
            return redirect(redirect_url)
        else:
            return view_func(request, *args, **kwargs)
    return wrapper



oauth = OAuth()
oauth.register(
    "auth0",
    client_id = os.environ['AUTH0_CLIENT_ID'],
    client_secret = os.environ['AUTH0_CLIENT_SECRET'],
    client_kwargs={
        "scope": "openid profile email",
    },
    server_metadata_url=f"https://{os.environ['AUTH0_DOMAIN']}/.well-known/openid-configuration",
)


## Auth0 Authentication Functions ##

def callback(request):
    token = oauth.auth0.authorize_access_token(request)
    request.session["user"] = token
    
    print(f"User Details: {token}")

    user_info = token['userinfo']
    user_email = user_info['email']
    user_auth_type = user_info['sub']
    user_email_verified = user_info['email_verified']
    user_name = user_info['name']
    updated_date_ts = user_info['iat']

    user_auth_objects = UserOAuth.objects.filter(email = user_email)
    print(f'Length of Auth Objects:', len(user_auth_objects))
    if len(user_auth_objects) > 0:
        user_auth_obj = user_auth_objects[0]
        user_auth_obj.email_verified = user_email_verified
        user_auth_obj.auth_type = user_auth_type
        user_auth_obj.name = user_name
        user_auth_obj.updated_at = updated_date_ts
        user_auth_obj.save()
        print('Saved USER AUTH OBJECT...')
    else:
        current_unix_ts = int(time.time())
        user_auth_obj = UserOAuth.objects.create(
            auth_type = user_auth_type,
            email = user_email,
            email_verified = user_email_verified,
            name = user_name,
            created_at = current_unix_ts,
            updated_at = updated_date_ts
        )
        user_auth_obj.save()
        print('Saved USER AUTH OBJECT...')


    print('DONE....')
    return redirect(request.build_absolute_uri(reverse("dashboard")))


def login(request):
    return oauth.auth0.authorize_redirect(
        request, request.build_absolute_uri(reverse("callback"))
    )


def logout(request):
    request.session.clear()

    return redirect(
        f"https://{os.environ['AUTH0_DOMAIN']}/v2/logout?"
        + urlencode(
            {
                "returnTo": request.build_absolute_uri(reverse("landing")),
                "client_id": os.environ['AUTH0_CLIENT_ID'],
            },
            quote_via=quote_plus,
        ),
    )




## Primary View Functions ##

def landing(request):
    initial_user_session = request.session.get("user")
    return render(request, 'landing.html',  {
        'user_session': initial_user_session
    })


def about(request):
    initial_user_session = request.session.get("user")
    return render(request, 'about.html', {
        'user_session': initial_user_session
    })


def playground(request):
    initial_user_session = request.session.get("user")

    code_id = request.GET.get('cid', None)
    lqid = request.GET.get('lqid', None)

    user_oauth_obj = None
    if initial_user_session is not None:
        user_oauth_obj = UserOAuth.objects.get(email = initial_user_session['userinfo']['email'])

    ls_q_obj = None
    ls_q_test_case_examples = []
    if lqid is not None:
        ls_q_obj = get_object_or_404(LessonQuestion, id = lqid)
        ls_q_test_case_examples = LessonQuestionTestCase.objects.filter(lesson_question_obj = ls_q_obj)
        print(ls_q_test_case_examples)
        # ls_q_obj = get_object_or_404(NewPracticeQuestion, id = lqid)
        # ls_q_test_case_examples = NewPracticeTestCase.objects.filter(question_obj = ls_q_obj)

    
    user_is_admin = request.user.is_superuser
    if user_is_admin:  # exempt from auth check; has visibility into all user's code
        uc_objects = UserCode.objects.filter(
            id = code_id
        )
    else:
        uc_objects = UserCode.objects.filter(
            id = code_id,
            user_auth_obj = user_oauth_obj
        )

    user_conversation_objects = []
    if len(uc_objects) > 0:
        uc_obj = uc_objects[0]
        if user_is_admin:
            user_conversation_objects = UserConversation.objects.filter(
                code_obj = uc_obj
            ).order_by('created_at')
        else:
            user_conversation_objects = UserConversation.objects.filter(
                code_obj = uc_obj,
                user_auth_obj = user_oauth_obj
            ).order_by('created_at')
    else:
        uc_obj = None
        if ls_q_obj is not None:
            lesson_code_objects = UserCode.objects.filter(
                lesson_question_obj = ls_q_obj,
                user_auth_obj = user_oauth_obj
            )
            if len(lesson_code_objects) == 1:  # should always be 1
                uc_obj = lesson_code_objects[0]


    return render(request, 'playground.html', {
        'user_session': initial_user_session,
        'code_id': code_id,
        'uc_obj': uc_obj,
        'user_conversation_objects': user_conversation_objects,
        'qid': lqid,
        'lesson_question_object': ls_q_obj,
        'lesson_question_test_cases': ls_q_test_case_examples
    })



def lesson_dashboard(request):
    initial_user_session = request.session.get("user")
    lesson_objects = Lesson.objects.all().order_by('created_at')

    return render(request, 'lesson_dashboard.html', {
        'user_session': initial_user_session,
        'lesson_objects': lesson_objects
    })



def questions(request, lid):
    
    initial_user_session = request.session.get("user")

    user_auth_obj = None
    if initial_user_session is not None:
        user_auth_obj = UserOAuth.objects.get(email = initial_user_session['userinfo']['email'])


    lesson_obj = get_object_or_404(Lesson, id = lid)
    lesson_questions = LessonQuestion.objects.filter(
        lesson_obj = lesson_obj
    )

    final_lesson_questions_rv = []
    for ls_q_obj in lesson_questions:
        
        uc_code_objects = []
        if user_auth_obj is not None:
            uc_code_objects = UserCode.objects.filter(
                lesson_question_obj = ls_q_obj,
                user_auth_obj = user_auth_obj
            )

        if len(uc_code_objects) > 0:
            final_lesson_questions_rv.append({
                'user_code': True,
                'lesson_question_obj': ls_q_obj,
                'user_code_obj': uc_code_objects[0]
            })
        else:
            final_lesson_questions_rv.append({
                'user_code': False,
                'lesson_question_obj': ls_q_obj
            })


    return render(request, 'questions.html', {
        'user_session': initial_user_session,
        'lesson_object': lesson_obj,
        'lesson_formatted_description': lesson_obj.description.replace('\n', '<br/><br/>').replace('|', '<br/>'),
        # 'lesson_questions': lesson_questions
        'lesson_questions': final_lesson_questions_rv
    })



def practice_questions(request):
    # np_questions = NewPracticeQuestion.objects.all()
    lesson_obj = Lesson.objects.get(title = 'new_void')
    np_questions = LessonQuestion.objects.filter(lesson_obj = lesson_obj).order_by('created_at')

    initial_user_session = request.session.get("user")

    return render(request, 'lesson_dashboard_new.html', {
        'user_session': initial_user_session,
        'questions': np_questions,
    })


@user_authentication_required
def dashboard(request):
    initial_user_session = request.session.get("user")
    user_oauth_obj = UserOAuth.objects.get(email = initial_user_session['userinfo']['email'])
    # user_conversations = UserConversation.objects.filter(
    #     user_auth_obj = user_oauth_obj
    # )

    user_code_objects = UserCode.objects.filter(
        user_auth_obj = user_oauth_obj
    ).order_by('-created_at')
    
    final_rv = []
    for uc_obj in user_code_objects:
        us_conv_objects_count = UserConversation.objects.filter(code_obj = uc_obj).count()

        # if len(us_conv_objects) > 0:
        #     usr_conv_obj = us_conv_objects[0]
        # else:
        #     usr_conv_obj = None
        
        final_rv.append({
            'code_obj': uc_obj,
            'user_conv_obj_count': us_conv_objects_count
        })

    return render(request, 'dashboard.html',  {
        'user_session': initial_user_session,
        'user_code_list': final_rv
        # 'user_code_objects': user_code_objects
        # 'user_conversations': user_conversations
    })



def handle_user_message(request):

    initial_user_session = request.session.get("user")

    if request.method == 'POST':

        # print('form-data:', request.POST)

        user_question = request.POST['message'].strip()
        user_code = request.POST['user_code'].strip()
        user_cid = request.POST['cid']
        user_lqid = request.POST['lqid']

        initial_user_session = request.session.get('user')
        if initial_user_session is None:
            return JsonResponse({'success': False, 'message': 'user is not authenticated.'})


        lesson_ques_obj = None
        if user_lqid != 'None':
            lesson_question_objects = LessonQuestion.objects.filter(id = user_lqid)
            if len(lesson_question_objects) > 0:
                lesson_ques_obj = lesson_question_objects[0]


        user_oauth_obj = UserOAuth.objects.get(email = initial_user_session['userinfo']['email'])
        prev_conversation_history = []
        if user_cid != 'None':

            prev_conversation_messages = UserConversation.objects.filter(
                code_obj_id = user_cid,
                user_auth_obj = user_oauth_obj
            ).order_by('created_at')

            if len(prev_conversation_messages) > 0:
                for uc_obj in prev_conversation_messages[:5]:
                    uc_question = uc_obj.question
                    uc_response = uc_obj.response
                    prev_conversation_history.append(f"Question: { uc_question }")
                    prev_conversation_history.append(f"Response: { uc_response }")


        prev_conversation_st = ''
        if len(prev_conversation_history) > 0:
            prev_conversation_st = '\n'.join(prev_conversation_history)
        
        # print('Previous Chat String:', prev_conversation_st)

        model_response_dict = main_utils.main_handle_question(
            question = user_question,
            student_code = user_code,
            previous_chat_history_st = prev_conversation_st
        )
        # print('model-response:', model_response_dict)

        if user_cid == 'None':
            
            if user_lqid == 'None':
                rnd_code_filename = ''.join([secrets.choice(string.ascii_lowercase) for idx in range(10)])
            else:
                rnd_code_filename = lesson_ques_obj.question_name

            uc_obj = UserCode.objects.create(
                user_auth_obj = user_oauth_obj,
                code_unique_name = rnd_code_filename,
                user_code = user_code,
                lesson_question_obj = lesson_ques_obj
            )
            uc_obj.save()
            
            ur_obj = UserConversation.objects.create(
                user_auth_obj = user_oauth_obj,
                code_obj = uc_obj,
                question = model_response_dict['question'],
                question_prompt = model_response_dict['q_prompt'],
                response = model_response_dict['response'],
            )
            ur_obj.save()

        else:
            # uc_obj = UserCode.objects.get(id = user_cid)
            # uc_obj.user_code = user_code
            # uc_obj.save()

            uc_objects = UserCode.objects.filter(id = user_cid, user_auth_obj = user_oauth_obj)
            if len(uc_objects) == 0:
                return JsonResponse({'success': False, 'response': 'Object id not found.'})

            uc_obj = uc_objects[0]
            uc_obj.lesson_question_obj = lesson_ques_obj
            uc_obj.user_code = user_code
            uc_obj.save()

            ur_obj = UserConversation.objects.create(
                user_auth_obj = user_oauth_obj,
                code_obj = uc_obj,
                question = model_response_dict['question'],
                question_prompt = model_response_dict['q_prompt'],
                response = model_response_dict['response'],
            )
            ur_obj.save()

    
        model_response_dict['cid'] = uc_obj.id
        return JsonResponse({'success': True, 'response': model_response_dict})



def save_user_code(request):
    
    initial_user_session = request.session.get("user")

    if request.method == 'POST':

        if initial_user_session is not None:
            user_oauth_objects = UserOAuth.objects.filter(email = initial_user_session['userinfo']['email'])
            if len(user_oauth_objects) == 0:
                return JsonResponse({'success': False, 'response': 'User must be authenticated.'})
        else:
            return JsonResponse({'success': False, 'response': 'User must be authenticated.'})

        user_auth_obj = user_oauth_objects[0]
        user_code = request.POST['user_code'].strip()
        cid = request.POST['cid']
        lq_id = request.POST['lqid']

        lesson_ques_obj = None
        if lq_id != 'None':
            lesson_question_objects = LessonQuestion.objects.filter(id = lq_id)
            if len(lesson_question_objects) > 0:
                lesson_ques_obj = lesson_question_objects[0]

        if cid == 'None':
            
            if lq_id == 'None':
                rnd_code_filename = ''.join([secrets.choice(string.ascii_lowercase) for idx in range(10)])
            else:
                rnd_code_filename = lesson_ques_obj.question_name

            uc_obj = UserCode.objects.create(
                user_auth_obj = user_auth_obj,
                code_unique_name = rnd_code_filename,
                user_code = user_code,
                lesson_question_obj = lesson_ques_obj
            )
            uc_obj.save()
            return JsonResponse({'success': True, 'cid': uc_obj.id})

        else:
            # uc_obj = UserCode.objects.get(id = cid)
            uc_objects = UserCode.objects.filter(id = cid, user_auth_obj = user_auth_obj)
            if len(uc_objects) == 0:
                return JsonResponse({'success': False, 'response': 'Object id not found.'})
            
            uc_obj = uc_objects[0]
            uc_obj.lesson_question_obj = lesson_ques_obj
            uc_obj.user_code = user_code
            uc_obj.save()
            return JsonResponse({'success': True, 'cid': uc_obj.id})



# TODO: 
    # at the moment, file-name-change will only work if code object exists (ie. cid is not None)
        # fix this to save the code with the new file-name if the code obj doesn't exist
def handle_file_name_change(request):
    
    initial_user_session = request.session.get("user")

    if request.method == 'POST':
        
        user_oauth_objects = UserOAuth.objects.filter(email = initial_user_session['userinfo']['email'])
        if len(user_oauth_objects) == 0:
            return JsonResponse({'success': False, 'response': 'User must be authenticated.'})
        
        user_auth_obj = user_oauth_objects[0]
        new_file_name = request.POST['new_file_name'].strip()
        cid = request.POST['cid']


        uc_obj = UserCode.objects.get(
            id = cid,
            user_auth_obj = user_auth_obj
        )

        uc_obj.code_unique_name = new_file_name
        uc_obj.save()

        return JsonResponse({'success': True, 'cid': uc_obj.id, 'new_file_name': new_file_name})



def teacher_admin_dashboard(request):

    if not request.user.is_superuser:
        return redirect('landing')

    all_users = UserOAuth.objects.all()
    
    final_all_users_rv = []
    for uobj in all_users:
        code_count = UserCode.objects.filter(
            user_auth_obj = uobj
        ).count()
        conversation_count = UserConversation.objects.filter(
            user_auth_obj = uobj
        ).count()

        final_all_users_rv.append({
            'user_obj': uobj,
            'user_created_at': datetime.datetime.fromtimestamp(float(uobj.created_at)),
            'user_last_login_in': datetime.datetime.fromtimestamp(float(uobj.updated_at)),
            'code_count': code_count,
            'conversation_count': conversation_count
        })

    
    final_all_users_rv = sorted(final_all_users_rv, key=itemgetter('user_last_login_in'), reverse=True)

    return render(request, 'teacher_admin_dashboard.html', {
        'all_students': final_all_users_rv
    })



def teacher_admin_student_page(request, uid):
    
    if not request.user.is_superuser:
        return redirect('landing')

    user_auth_obj = get_object_or_404(UserOAuth, id = uid)

    final_user_rv = {}
    final_user_rv['user_obj'] = user_auth_obj
    final_user_rv['user_signup_date'] = datetime.datetime.fromtimestamp(float(user_auth_obj.created_at))
    final_user_rv['user_last_login_date'] = datetime.datetime.fromtimestamp(float(user_auth_obj.updated_at))
    
    user_code_objects = UserCode.objects.filter(
        user_auth_obj = user_auth_obj
    )

    final_code_rv = []
    for uc_obj in user_code_objects:
        user_conversation_objects = UserConversation.objects.filter(
            code_obj = uc_obj
        )
        final_code_rv.append([uc_obj, user_conversation_objects])

    # final_user_rv['user_code_objects'] = user_code_objects
    # final_user_rv['user_conversation_objects'] = user_conversation_objects

    final_user_rv['user_code_objects'] = final_code_rv

    return render(request, 'teacher_admin_student_view.html', final_user_rv)




def general_cs_tutor(request):

    # TODO: 
        # add pid param
        # test to ensure good
        # add the saved conversations in the dashboard tab
        # go from there

    initial_user_session = request.session.get("user")        

    # general_conv_parent_id = request.GET.get('pid', None)
    # ug_tut_parent_obj = None
    # if general_conv_parent_id is not None:
    #     ug_tut_parent_objects = UserGeneralTutorParent.objects.filter(id = general_conv_parent_id)
    #     if len(ug_tut_parent_objects) > 0:
    #         ug_tut_parent_obj = ug_tut_parent_objects[0]

    user_oauth_obj = None
    if initial_user_session is not None:
        user_oauth_obj = UserOAuth.objects.get(email = initial_user_session['userinfo']['email'])

    utc_objects = UserGeneralTutorConversation.objects.filter(
        user_auth_obj = user_oauth_obj
    ).order_by('created_at')

    return render(request, 'general_cs_tutor.html', {
        'user_session': initial_user_session,
        'user_conversation_objects': utc_objects,
    })



def handle_general_tutor_user_message(request):
    initial_user_session = request.session.get("user")

    if request.method == 'POST':
        print('form-data:', request.POST)

        initial_user_session = request.session.get('user')        
        
        if initial_user_session is None:
            return JsonResponse({'success': False, 'message': 'user is not authenticated.'})
        
        user_question = request.POST['message'].strip()
        # uc_parent_obj_id = request.POST['uc_parent_obj_id']
        # # user_ct_obj_id = request.POST['user_ct_obj_id']

        # user_oauth_obj = UserOAuth.objects.get(email = initial_user_session['userinfo']['email'])
        # ugt_parent_obj = None
        # if uc_parent_obj_id is None:
        #     ugt_parent_obj = UserGeneralTutorParent.objects.create(
        #         user_auth_obj = user_oauth_obj
        #     )
        #     ugt_parent_obj.sav()

        # else:
        #     ugt_parent_objects = UserGeneralTutorParent.objects.filter(
        #         id = uc_parent_obj_id,
        #         user_auth_obj = user_oauth_obj
        #     )
        #     if len(ugt_parent_objects) == 0:
        #         return JsonResponse({'success': False, 'message': 'Conversation not found.'})                
        #     else:
        #         ugt_parent_obj = ugt_parent_objects[0]


        # # prev_conversation_history = []
        # if uc_parent_obj_id != 'None':

        #     prev_conversation_messages = UserGeneralTutorConversation.objects.filter(
        #         user_auth_obj = user_oauth_obj,
        #         # gt_parent_obj = ugt_parent_obj
        #     ).order_by('created_at')

        #     if len(prev_conversation_messages) > 0:
        #         for uc_obj in prev_conversation_messages[:5]:
        #             uc_question = uc_obj.question
        #             uc_response = uc_obj.response
        #             prev_conversation_history.append(f"Question: { uc_question }")
        #             prev_conversation_history.append(f"Response: { uc_response }")


        user_oauth_obj = UserOAuth.objects.get(email = initial_user_session['userinfo']['email'])
        ug_tut_cv_objects = UserGeneralTutorConversation.objects.filter(
            user_auth_obj = user_oauth_obj,
        ).order_by('-created_at')

        prev_conversation_st = ''
        if len(ug_tut_cv_objects) > 0:
            prev_conversation_history = []
            for uc_tut_obj in ug_tut_cv_objects[:3]:
                uc_question = uc_tut_obj.question
                uc_response = uc_tut_obj.response
                prev_conversation_history.append(f"Question: { uc_question }")
                prev_conversation_history.append(f"Response: { uc_response }")

            prev_conversation_st = '\n'.join(prev_conversation_history).strip()
        

        print('PREVIOUS CONV:', prev_conversation_st)

        model_response_dict = main_utils.general_tutor_handle_question(
            question = user_question,
            previous_chat_history_st = prev_conversation_st
        )

        uct_obj = UserGeneralTutorConversation.objects.create(
            user_auth_obj = user_oauth_obj,
            question = model_response_dict['question'],
            question_prompt = model_response_dict['q_prompt'],
            response = model_response_dict['response'],
        )
        uct_obj.save()
        
        # model_response_dict['uct_parent_obj_id'] = ugt_parent_obj.id
        return JsonResponse({'success': True, 'response': model_response_dict})






### Teacher-Student-Section ###

def teacher_admin_signup(request):

    if request.session.get("teacher_object", None) is not None:
        return redirect('teacher_admin_dashboard')

    if request.method == 'POST':
        print('post-data:', request.POST)

        full_name = request.POST['full-name']
        email = request.POST['email']
        password_one = request.POST['password-one']
        password_two = request.POST['password-two']

        f = forms.EmailField()
        try:
            email = f.clean(email)
        except:
            user_errors = {
                'error_message': 'invalid email'
            }
            return render(request, 'teacher_signup.html', user_errors)

        if password_one != password_two:
            user_errors = {
                'error_message': "passwords don't match"
            }
            return render(request, 'teacher_signup.html', user_errors)

        hashed_pwd = make_password(password_one)
        th_obj = Teacher.objects.create(
            full_name = full_name.strip(),
            email = email,
            password = hashed_pwd
        )
        th_obj.save()

        request.session["teacher_object"] =  model_to_dict( th_obj )

        return redirect('teacher_admin_dashboard')


    return render(request, 'teacher_signup.html')



def teacher_admin_login(request):
    
    if request.session.get("teacher_object", None) is not None:
        return redirect('teacher_admin_dashboard')

    if request.method == 'POST':
        print('post-data:', request.POST)

        email = request.POST['email']
        password = request.POST['password']

        th_objects = Teacher.objects.filter(
            email = email
        )
        if len(th_objects) == 0:
            user_errors = {
                'error_message': "email not found"
            }
            return render(request, 'teacher_login.html', user_errors)

        th_obj = th_objects[0]
        hashed_pwd = th_obj.password

        valid_pw = check_password(password, hashed_pwd)
        if valid_pw:
            
            # request.session["teacher_object"] = th_obj
            request.session["teacher_object"] =  model_to_dict( th_obj )

            return redirect('teacher_admin_dashboard')

        else:
            user_errors = {
                'error_message': "invalid password"
            }
            return render(request, 'teacher_login.html', user_errors)


    return render(request, 'teacher_login.html')



def teacher_admin_dashboard(request):

    if request.session.get("teacher_object", None) is None:
        # TODO: redirect to landing for now as private-beta for improving teacher-db-functionality
        return redirect('landing')

    teacher_obj = request.session.get("teacher_object")
    teacher_obj = Teacher.objects.get(id = teacher_obj['id'])



    return render(request, 'teacher_admin_dashboard.html', {
        'teacher_obj': teacher_obj
    })




def teacher_admin_student_management(request):

    if request.session.get("teacher_object", None) is None:
        # TODO: redirect to landing for now as private-beta for improving teacher-db-functionality
        return redirect('landing')

    teacher_obj = request.session.get("teacher_object")
    teacher_obj = Teacher.objects.get(id = teacher_obj['id'])

    # asdkj@gmail.com, asdkjalk@gmail.com, asldkjalkd@gmail.com, aslkjalddalkj@gmail.com, aslkdja223@gmail.com, asldkjasdlkj@asdhoasod.com
    if request.method == "POST":
        print('post-data:', request.POST)

        # TODO: should add auth checks or safety check here on get()?
        teacher_obj = request.session.get("teacher_object")
        teacher_obj = Teacher.objects.get(id = teacher_obj['id'])

        student_emails = request.POST.getlist('student_emails')
        print('stud-emails:', student_emails)
        students_emails_list = student_emails[0].split(', ')

        emails_to_send_list = []
        for em in students_emails_list:
            sd_em = em.strip()

            # quick validation on the student emails entered
            f = forms.EmailField()
            try:
                email = f.clean(email)
            except:
                pass


            tsi_obj = TeacherStudentInvite.objects.create(
                student_email = sd_em,
                teacher_obj = teacher_obj
            )
            tsi_obj.save()

            emails_to_send_list.append(sd_em)

        # TODO:
            # to test this, create enterprise gmail account <-- current domain is fine
            # setup the password on that and go from there to test this functionality...

        # for eml in emails_to_send_list:
        #     current_site = get_current_site(request)
        #     message = render_to_string('student_account_create_email.html', {
        #         'teacher_name': teacher_obj.full_name,
        #         'domain': current_site.domain,
        #     })
        #     send_student_account_create_email.delay(
        #         message = message,
        #         user_email = eml
        #     )

        return render(request, 'teacher_admin_student_management.html', {
            'teacher_obj': teacher_obj,
            'invite_student_success': True
        })


    return render(request, 'teacher_admin_student_management.html', {
        'teacher_obj': teacher_obj
    })



def teacher_admin_question_management(request):
    if request.session.get("teacher_object", None) is None:
        # TODO: redirect to landing for now as private-beta for improving teacher-db-functionality
        return redirect('landing')

    teacher_obj = request.session.get("teacher_object")
    teacher_obj = Teacher.objects.get(id = teacher_obj['id'])

    return render(request, 'teacher_admin_question_management.html', {
        'teacher_obj': teacher_obj
    })


def teacher_admin_assistant_chat(request):
    if request.session.get("teacher_object", None) is None:
        # TODO: redirect to landing for now as private-beta for improving teacher-db-functionality
        return redirect('landing')

    teacher_obj = request.session.get("teacher_object")
    teacher_obj = Teacher.objects.get(id = teacher_obj['id'])

    return render(request, 'teacher_admin_assistant_chat.html', {
        'teacher_obj': teacher_obj
    })



def student_admin_account_create(request):
    # TODO: 
        # also add logic to ensure the student account isn't already registered
        # if it is, redirecto to the studnt_admin_account_login
    
    # student will be prompted to enter email
        # then, if email valid, show the account create, else, show error message 

    print('data:', request.POST)

    if request.method == "POST":
    
        if 'form_type' in request.POST:

            if request.POST['form_type']  == 'validate_user_email':
                student_email = request.POST['student_email'].strip()
                tsi_objects = TeacherStudentInvite.objects.filter(
                    student_email = student_email
                )
                if len(tsi_objects) > 0:
                    tsi_obj = tsi_objects[0]
                    return JsonResponse({'success': True})
                else:
                    return JsonResponse({'success': False, 'message': 'Student not found.'})

        else:
            print('user-signup-data:', request.POST)

            student_full_name = request.POST['full-name']
            student_email = request.POST['email']
            student_password = request.POST['password-one']
            student_password_two = request.POST['password-two']

            student_objects = Student.objects.filter(
                email = student_email
            )
            if len(student_objects) > 0:
                return JsonResponse({'success': False, 'message': 'Student Account already exists.'})

            f = forms.EmailField()
            try:
                student_email = f.clean(student_email)
            except:
                user_errors = {
                    'error_message': 'invalid email',
                    'form_type': 'account_create_form'
                }
                return render(request, 'teacher_signup.html', user_errors)

            if student_password != student_password_two:
                user_errors = {
                    'error_message': "passwords don't match",
                    'form_type': 'account_create_form'
                }
                return render(request, 'teacher_signup.html', user_errors)


            tsi_obj = TeacherStudentInvite.objects.get(student_email = student_email)
            hashed_pwd = make_password(student_password)

            sd_obj = Student.objects.create(
                full_name = student_full_name,
                teacher_obj = tsi_obj.teacher_obj,
                email = student_email, 
                password = hashed_pwd
            )
            sd_obj.save()

            request.session["student_object"] = model_to_dict( sd_obj )
            return redirect('student_admin_dashboard')

    return render(request, 'student_admin_account_create.html')



def student_admin_login(request):
    
    if request.session.get("student_object", None) is not None:
        return redirect('student_admin_dashboard')

    if request.method == 'POST':

        email = request.POST['email']
        password = request.POST['password']

        std_objects = Student.objects.filter(
            email = email
        )
        if len(std_objects) == 0:
            user_errors = {
                'error_message': "email not found."
            }
            return render(request, 'student_admin_login.html', user_errors)

        std_obj = std_objects[0]
        hashed_pwd = std_obj.password

        valid_pw = check_password(password, hashed_pwd)
        if valid_pw:
            request.session["student_object"] = model_to_dict( std_obj )
            return redirect('student_admin_dashboard')
        else:
            user_errors = {
                'error_message': "invalid password"
            }
            return render(request, 'student_admin_login.html', user_errors)


    return render(request, 'student_admin_login.html')



def student_admin_dashboard(request):

    if request.session.get("student_object", None) is None:
        return redirect('student_admin_login')

    return render(request, 'student_admin_dashboard.html')






# def handle_code_submit(request):

#     initial_user_session = request.session.get("user")

#     if request.method == 'POST':
#         # TODO: 
#             # first, update the code, etc.
#             # then, pass to gpt with question as, 'this is my final solution, is it correct? can you provide feedback?'
        
#         initial_user_session = request.session.get("user")
#         if initial_user_session is not None:
#             user_oauth_objects = UserOAuth.objects.filter(email = initial_user_session['userinfo']['email'])
#             if len(user_oauth_objects) == 0:
#                 return JsonResponse({'success': False, 'response': 'User must be authenticated.'})
#         else:
#             return JsonResponse({'success': False, 'response': 'User must be authenticated.'})

#         user_auth_obj = user_oauth_objects[0]
#         user_code = request.POST['user_code'].strip()
#         cid = request.POST['cid']
#         lq_id = request.POST['lqid']

#         lesson_ques_obj = None
#         lesson_question_objects = LessonQuestion.objects.filter(id = lq_id)
#         if len(lesson_question_objects) > 0:
#             lesson_ques_obj = lesson_question_objects[0]

#         ## Saving/Updating User Code
#         if cid == 'None':
#             rnd_code_filename = ''.join([secrets.choice(string.ascii_lowercase) for idx in range(10)])
#             uc_obj = UserCode.objects.create(
#                 user_auth_obj = user_auth_obj,
#                 code_unique_name = rnd_code_filename,
#                 user_code = user_code,
#                 lesson_question_obj = lesson_ques_obj
#             )
#             uc_obj.save()

#         else:
#             # uc_obj = UserCode.objects.get(id = cid)
#             uc_objects = UserCode.objects.filter(id = cid, user_auth_obj = user_auth_obj)
#             if len(uc_objects) == 0:
#                 return JsonResponse({'success': False, 'response': 'Object id not found.'})
            
#             uc_obj = uc_objects[0]
#             uc_obj.lesson_question_obj = lesson_ques_obj
#             uc_obj.user_code = user_code
#             uc_obj.save()

        
#         ## Asking GPT to generate feedback

#         model_response_dict = main_utils.main_handle_question(
#             question = user_question,
#             student_code = user_code,
#             previous_chat_history_st = prev_conversation_st
#         )

