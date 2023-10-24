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
import uuid
import time
import functools
import secrets
import string
import datetime
from dotenv import load_dotenv, find_dotenv
from operator import itemgetter
from authlib.integrations.django_client import OAuth
import pinecone

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





## Primary General View Functions ##

# def new_landing_main(request):
#     initial_user_session = request.session.get("user")
#     # return render(request, 'landing.html',  {
#     return render(request, 'new_landing_main_one.html',  {        
#         'user_session': initial_user_session
#     })




## Primary View Functions ##

def test_page(request):
    return render(request, 'test_page.html')


def landing_email_subscribe_handle(request):
    if request.method == 'POST':
        print('email-post:', request.POST)

        user_email = request.POST['user_email'].strip()
        le_obj = LandingEmailSubscription.objects.create(
            email = user_email
        )
        le_obj.save()

        return JsonResponse({'success': True})



def landing(request):
    initial_user_session = request.session.get("user")
    
    return render(request, 'new_landing_main_three.html',  {
        'user_session': initial_user_session
    })


def about(request):
    initial_user_session = request.session.get("user")
    return render(request, 'new_about.html', {
        'user_session': initial_user_session
    })



def playground(request):
    initial_user_session = request.session.get("user")

    code_id = request.GET.get('cid', None)
    lqid = request.GET.get('lqid', None)
    
    pclid = request.GET.get('pclid', None)


    user_oauth_obj = None
    if initial_user_session is not None:
        user_oauth_obj = UserOAuth.objects.get(email = initial_user_session['userinfo']['email'])


    pt_course_lesson_question_obj = None
    pt_course_test_case_examples = []
    if pclid is not None:
        # PythonLessonQuestion.objects
        pt_course_lesson_question_obj = get_object_or_404(PythonLessonQuestion, id = pclid)
        pt_course_test_case_examples = PythonLessonQuestionTestCase.objects.filter(
            lesson_question_obj = pt_course_lesson_question_obj
        )



    ls_q_obj = None
    ls_q_test_case_examples = []
    if lqid is not None:
        ls_q_obj = get_object_or_404(LessonQuestion, id = lqid)
        ls_q_test_case_examples = LessonQuestionTestCase.objects.filter(lesson_question_obj = ls_q_obj)
        print(ls_q_test_case_examples)
        # ls_q_obj = get_object_or_404(NewPracticeQuestion, id = lqid)
        # ls_q_test_case_examples = NewPracticeTestCase.objects.filter(question_obj = ls_q_obj)


    student_assigned_qid = request.GET.get('stdqid', None)
    tq_obj = None
    tq_obj_test_case_examples = []
    if student_assigned_qid is not None:
        tq_obj = get_object_or_404(TeacherQuestion, id = student_assigned_qid)
        tq_obj_test_case_examples = TeacherQuestionTestCase.objects.filter(teacher_question_obj = tq_obj)

    
    # if request.session.get("student_object", None) is None:
    #     return JsonResponse({'success': False, 'message': 'Not Authorized.'})
    # student_obj_session = request.session['student_object']
    # student_obj = Student.objects.get(id = student_obj_session['id'])
        
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


    initial_rnd_file_name = ''.join([secrets.choice(string.ascii_lowercase) for idx in range(6)])
    print('rnd filename:', initial_rnd_file_name)

    return render(request, 'playground.html', {
        'user_session': initial_user_session,
        'code_id': code_id,
        'uc_obj': uc_obj,
        'user_conversation_objects': user_conversation_objects,
        'qid': lqid,
        'lesson_question_object': ls_q_obj,
        'lesson_question_test_cases': ls_q_test_case_examples,
        'stdqid': student_assigned_qid,
        'teacher_question_object': tq_obj,
        'teacher_question_test_cases': tq_obj_test_case_examples,
        'initial_rnd_file_name': initial_rnd_file_name,
        # 'student_obj': student_obj

        'pclid': pclid,
        'pt_course_lesson_question_obj': pt_course_lesson_question_obj,
        'pt_course_test_case_examples': pt_course_test_case_examples

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

    
    user_file_objects = UserFiles.objects.filter(
        user_auth_obj = user_oauth_obj
    ).order_by('-uploaded_at')
    print(user_file_objects)

    return render(request, 'dashboard.html',  {
        'user_session': initial_user_session,
        'user_code_list': final_rv,
        'user_file_objects': user_file_objects
        # 'user_code_objects': user_code_objects
        # 'user_conversations': user_conversations
    })



def handle_user_message(request):

    initial_user_session = request.session.get("user")

    if request.method == 'POST':

        # print('form-data:', request.POST)

        user_question = request.POST['message'].strip()
        user_code = request.POST['user_code'].strip()     
        user_code = user_code.replace('`', '"').strip()

        initial_user_session = request.session.get('user')
        if initial_user_session is None:

            # TODO: get the messages from localstorage here

            previous_message_st = request.POST['previous_messages'].strip()

            model_response_dict = main_utils.main_handle_question(
                question = user_question,
                student_code = user_code,
                previous_chat_history_st = previous_message_st
            )
            # print('model-response:', model_response_dict)
            # return JsonResponse({'success': False, 'message': 'user is not authenticated.'})
            # model_response_dict['cid'] = uc_obj.id
            return JsonResponse({'success': True, 'response': model_response_dict})


        user_cid = request.POST['cid']
        user_lqid = request.POST['lqid']
        # user_pclid = request.POST['pclid']

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
            ).order_by('-created_at')

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
        user_code = user_code.replace('`', '"').strip()
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



def handle_file_name_change(request):
    
    initial_user_session = request.session.get("user")

    if request.method == 'POST':
        
        user_oauth_objects = UserOAuth.objects.filter(email = initial_user_session['userinfo']['email'])
        if len(user_oauth_objects) == 0:
            return JsonResponse({'success': False, 'response': 'User must be authenticated.'})
        
        user_auth_obj = user_oauth_objects[0]
        new_file_name = request.POST['new_file_name'].strip()
        cid = request.POST['cid']
        lqid = request.POST['lqid']
        user_code = request.POST['user_code'].strip()
        user_code = user_code.replace('`', '"').strip()

        lesson_ques_obj = None
        if lqid != 'None':
            lesson_question_objects = LessonQuestion.objects.filter(id = lqid)
            if len(lesson_question_objects) > 0:
                lesson_ques_obj = lesson_question_objects[0]

        if cid == 'None':
            uc_obj = UserCode.objects.create(
                user_auth_obj = user_auth_obj,
                code_unique_name = new_file_name,
                user_code = user_code,
                lesson_question_obj = lesson_ques_obj
            )
            uc_obj.save()

        else:
            uc_obj = UserCode.objects.get(
                id = cid,
                user_auth_obj = user_auth_obj
            )
            uc_obj.code_unique_name = new_file_name
            uc_obj.save()

        return JsonResponse({'success': True, 'cid': uc_obj.id, 'new_file_name': new_file_name})



# def teacher_admin_dashboard(request):
# # def super_user_admin_dashboard(request):

#     # if not request.user.is_superuser:
#     #     return redirect('landing')

#     all_users = UserOAuth.objects.all()
    
#     final_all_users_rv = []
#     for uobj in all_users:
#         code_count = UserCode.objects.filter(
#             user_auth_obj = uobj
#         ).count()
#         conversation_count = UserConversation.objects.filter(
#             user_auth_obj = uobj
#         ).count()

#         final_all_users_rv.append({
#             'user_obj': uobj,
#             'user_created_at': datetime.datetime.fromtimestamp(float(uobj.created_at)),
#             'user_last_login_in': datetime.datetime.fromtimestamp(float(uobj.updated_at)),
#             'code_count': code_count,
#             'conversation_count': conversation_count
#         })

    
#     final_all_users_rv = sorted(final_all_users_rv, key=itemgetter('user_last_login_in'), reverse=True)

#     return render(request, 'teacher_admin_dashboard.html', {
#         'all_students': final_all_users_rv
#     })



# # def teacher_admin_student_page(request, uid):
# def super_user_admin_student_page(request, uid):
    
#     if not request.user.is_superuser:
#         return redirect('landing')

#     user_auth_obj = get_object_or_404(UserOAuth, id = uid)

#     final_user_rv = {}
#     final_user_rv['user_obj'] = user_auth_obj
#     final_user_rv['user_signup_date'] = datetime.datetime.fromtimestamp(float(user_auth_obj.created_at))
#     final_user_rv['user_last_login_date'] = datetime.datetime.fromtimestamp(float(user_auth_obj.updated_at))
    
#     user_code_objects = UserCode.objects.filter(
#         user_auth_obj = user_auth_obj
#     )

#     final_code_rv = []
#     for uc_obj in user_code_objects:
#         user_conversation_objects = UserConversation.objects.filter(
#             code_obj = uc_obj
#         )
#         final_code_rv.append([uc_obj, user_conversation_objects])

#     # final_user_rv['user_code_objects'] = user_code_objects
#     # final_user_rv['user_conversation_objects'] = user_conversation_objects

#     final_user_rv['user_code_objects'] = final_code_rv

#     return render(request, 'teacher_admin_student_view.html', final_user_rv)




def general_cs_tutor(request):

    initial_user_session = request.session.get("user")        

    # general_conv_parent_id = request.GET.get('pid', None)
    # ug_tut_parent_obj = None
    # if general_conv_parent_id is not None:
    #     ug_tut_parent_objects = UserGeneralTutorParent.objects.filter(id = general_conv_parent_id)
    #     if len(ug_tut_parent_objects) > 0:
    #         ug_tut_parent_obj = ug_tut_parent_objects[0]

    user_oauth_obj = None
    utc_objects = None
    if initial_user_session is not None:
        user_oauth_obj = UserOAuth.objects.get(email = initial_user_session['userinfo']['email'])

        utc_objects = UserGeneralTutorConversation.objects.filter(
            user_auth_obj = user_oauth_obj
        ).order_by('created_at')


    return render(request, 'general_cs_tutor.html', {
        'user_session': initial_user_session,
        'user_conversation_objects': utc_objects,
    })



from gpt_learning_assistant.settings import MAX_FILE_SIZE



def handle_user_file_upload(request):
    # File Upload
    if request.method == 'POST':

        print('file-post:', request.POST, request.FILES)

        initial_user_session = request.session.get("user")
        if initial_user_session is None:
            return JsonResponse({'success': False, 'message': 'User must be authenticated.'})
        
        user_oauth_obj = None
        if initial_user_session is not None:
            user_oauth_obj = UserOAuth.objects.get(email = initial_user_session['userinfo']['email'])

        user_fn = request.POST['user_file_name'].strip()
        user_file_obj = request.FILES['user_file']

        if len(user_fn) == 0:
            return JsonResponse({'success': False, 'message': 'File Name must be greater than 0.'})

        if user_file_obj.size > MAX_FILE_SIZE:
            return JsonResponse({'success': False, 'message': 'Upload file too large.'})


        extracted_text_list = main_utils.extract_text_from_pdf(user_file_obj)
        print(f"Length of text list: {len(extracted_text_list)}")

        uf_obj = UserFiles.objects.create(
            user_auth_obj = user_oauth_obj,
            file_name = user_fn,
            file_path = user_file_obj
        )
        uf_obj.save()


        print(f"Computing embeddings for the extracted text...")
        main_txt_embd_list = []        
        for page_num in range(0, len(extracted_text_list)):

            txt = extracted_text_list[page_num]
            txt_num_tokens = len(txt)
            if txt_num_tokens > 8191:
                txt_max_bs = 8191
                for txt_idx in range(0, txt_num_tokens, txt_max_bs):
                    bt_txt = txt[txt_idx:txt_idx+txt_max_bs]
                    bt_txt_embd = main_utils.get_embedding(bt_txt)

                    main_txt_embd_list.append({
                        'page_number': page_num,
                        'text': bt_txt,
                        'embd': bt_txt_embd
                    })
            else:
                txt_embd = main_utils.get_embedding(txt)
                main_txt_embd_list.append({
                    'page_number': page_num,
                    'text': txt,
                    'embd': txt_embd
                })


        print(f"Preparing/Inserting to the pinecone index...")
        new_pinecone_list = []
        for idx in range(len(main_txt_embd_list)):
            t_embd_dict = main_txt_embd_list[idx]
            st_id = uuid.uuid4().hex
            new_pinecone_list.append({
                "id": st_id,
                "values": t_embd_dict['embd'],
                "metadata": {
                    "page_number": t_embd_dict['page_number'],
                    "page_text": t_embd_dict['text']
                }
            })


        rnd_namespace_name = uuid.uuid4().hex
        pinecone.init(
	        api_key = os.environ['PINECONE_API_KEY'],
	        environment = os.environ['PINECONE_ENVIRONMENT_NAME']
        )
        index = pinecone.Index('companion-app-main')
        pc_insert_response = index.upsert(
            new_pinecone_list,
            namespace = rnd_namespace_name
        )
        print('pinecone-insert-response:', pc_insert_response)

        fpc_obj = FilePineCone.objects.create(
            user_auth_obj = user_oauth_obj,
            file_obj = uf_obj,
            file_namespace = rnd_namespace_name
        )
        fpc_obj.save()

        return JsonResponse({'success': True, 'fid': uf_obj.id})



def user_file_viewer(request, file_id):
    
    initial_user_session = request.session.get("user")
    if initial_user_session is None:
        return redirect('landing')


    user_oauth_obj = UserOAuth.objects.get(email = initial_user_session['userinfo']['email'])
    fn_objects = UserFiles.objects.filter(id = file_id, user_auth_obj = user_oauth_obj)
    if len(fn_objects) == 0:
        return redirect('dashboard')

    fn_obj = fn_objects[0]

    user_file_conversations = UserFileConversation.objects.filter(
        user_auth_obj = user_oauth_obj,
        file_obj = fn_obj
    )

    return render(request, 'user_file_view.html', {
        'user_session': initial_user_session,
        'fn_obj': fn_obj,
        'user_file_conversations': user_file_conversations
    })



def handle_user_file_question(request):
        
    if request.method == 'POST':
        print('user-message:', request.POST)

        initial_user_session = request.session.get("user")
        if initial_user_session is None:
            return JsonResponse({'success': False, 'message': 'User must be authenticated.'})
        
        user_oauth_obj = None
        if initial_user_session is not None:
            user_oauth_obj = UserOAuth.objects.get(email = initial_user_session['userinfo']['email'])


        fid = request.POST['fid']
        user_message = request.POST['message'].strip()

        initial_user_session = request.session.get("user")
        user_oauth_obj = UserOAuth.objects.get(email = initial_user_session['userinfo']['email'])
        fn_objects = UserFiles.objects.filter(id = fid, user_auth_obj = user_oauth_obj)
        if len(fn_objects) == 0:
            return JsonResponse({'success': False, 'message': 'File not found.'})
        

        fn_obj = fn_objects[0]
        fn_pc_obj = FilePineCone.objects.get(file_obj = fn_obj)


        user_file_conversations = UserFileConversation.objects.filter(
            user_auth_obj = user_oauth_obj,
            file_obj = fn_obj
        ).order_by('-created_at')

        prev_conversation_st = ''
        if len(user_file_conversations) > 0:
            prev_conversation_history = []
            for uc_tut_obj in user_file_conversations[:1]:
                uc_question = uc_tut_obj.question
                uc_response = uc_tut_obj.response
                prev_conversation_history.append(f"Question: { uc_question }")
                prev_conversation_history.append(f"Response: { uc_response }")

            prev_conversation_st = '\n'.join(prev_conversation_history).strip()

        user_q_res_dict = main_utils.pinecone_handle_question(
            question = user_message,
            previous_chat_history_st = prev_conversation_st,
            pc_namespace = fn_pc_obj.file_namespace,
            k = 3
        )
        retrieved_page_number_list = [tmpd['page_number'] for tmpd in user_q_res_dict['reference_list']]

        ur_obj = UserFileConversation.objects.create(
            user_auth_obj = user_oauth_obj,
            file_obj = fn_obj,
            question = user_q_res_dict['question'],
            question_prompt = user_q_res_dict['q_prompt'],
            retrieved_numbers_list = retrieved_page_number_list,
            response = user_q_res_dict['response'],
            response_with_citations = user_q_res_dict['final_text_response']
        )
        ur_obj.save()

        return JsonResponse({'success': True, 'response': user_q_res_dict})






def handle_general_tutor_user_message(request):
    initial_user_session = request.session.get("user")

    if request.method == 'POST':        
        # if initial_user_session is None:
        #     return JsonResponse({'success': False, 'message': 'user is not authenticated.'})
                
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


        user_question = request.POST['message'].strip()
        initial_user_session = request.session.get('user')

        prev_conversation_st = ''
        user_oauth_obj = None
        if initial_user_session is None:
            user_oauth_obj = None
            # TODO: start here; get the landing page general-assistant complete; go from there to edit the assistant page
                # prioritize next eng steps from there (**super important)
            prev_conversation_st = request.POST['prev_conversation_history_st']

        else:                
            user_oauth_obj = UserOAuth.objects.get(email = initial_user_session['userinfo']['email'])

            ug_tut_cv_objects = UserGeneralTutorConversation.objects.filter(
                user_auth_obj = user_oauth_obj,
            ).order_by('-created_at')

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

        if user_oauth_obj is not None:
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

        # duplicate email check
        existing_teacher_objects = Teacher.objects.filter(email = email).count()
        if existing_teacher_objects > 0:
            user_errors = {
                'error_message': "Email already registered. Try to login instead."
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
        'teacher_obj': teacher_obj,
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

            # want to prevent duplicates
            tsi_existing_objects = TeacherStudentInvite.objects.filter(
                student_email = sd_em,
                teacher_obj = teacher_obj
            )
            if len(tsi_existing_objects) == 0:

                tsi_obj = TeacherStudentInvite.objects.create(
                    student_email = sd_em,
                    teacher_obj = teacher_obj
                )
                tsi_obj.save()

                emails_to_send_list.append(sd_em)


        for eml in emails_to_send_list:
            current_site = get_current_site(request)

            if 'code' in current_site.domain:
                hp_protocol = 'https'
            else:
                hp_protocol = 'http'

            message = render_to_string('student_account_create_email.html', {
                'teacher_name': teacher_obj.full_name,
                'domain': current_site.domain,
                'hp_protocol': hp_protocol
            })
            send_student_account_create_email.delay(
                message = message,
                user_email = eml
            )

        # return render(request, 'teacher_admin_student_management.html', {
        #     'teacher_obj': teacher_obj,
        #     'invite_student_success': True
        # })


    # associated_student_objects = Student.objects.filter(
    #     teacher_obj = teacher_obj
    # )
    # registered_students = Student.objects.filter(teacher_obj = teacher_obj)
    # invited_students_not_registered = TeacherStudentInvite.objects.filter(teacher_obj = teacher_obj, student_registered = False)

    all_invited_students = TeacherStudentInvite.objects.filter(teacher_obj = teacher_obj).order_by('-modified_at').order_by('-student_registered')
    all_registered_students = Student.objects.filter(teacher_obj = teacher_obj)

    final_student_rv = []
    for sd_obj in all_invited_students:
        if sd_obj.student_registered:
            reg_student_obj = Student.objects.get(email = sd_obj.student_email)
            
            num_code_files = StudentPlaygroundCode.objects.filter(student_obj = reg_student_obj).count()
            num_messages = 0
            num_messages += StudentPlaygroundConversation.objects.filter(student_obj = reg_student_obj).count()
            num_messages += StudentConversation.objects.filter(student_obj = reg_student_obj).count()

            final_student_rv.append([
                sd_obj, reg_student_obj, num_messages, num_code_files
            ])
        else:
            final_student_rv.append([
                sd_obj
            ])

    return render(request, 'teacher_admin_student_management.html', {
        'teacher_obj': teacher_obj,
        # 'student_objects': all_invited_students,
        # 'all_registered_students': all_registered_students
        'student_objects': final_student_rv
    })



def teacher_admin_question_management(request):
    if request.session.get("teacher_object", None) is None:
        # TODO: redirect to landing for now as private-beta for improving teacher-db-functionality
        return redirect('landing')

    teacher_obj = request.session.get("teacher_object")
    teacher_obj = Teacher.objects.get(id = teacher_obj['id'])

    if request.method == 'POST':
        print(request.POST)

        question_name = request.POST['question-name'].strip()
        question_text = request.POST['question-text'].strip()

        tc_input_one, tc_output_one = request.POST['test-input-one'].strip(), request.POST['test-output-one'].strip()
        tc_input_two, tc_output_two = request.POST['test-input-two'].strip(), request.POST['test-output-two'].strip()
        tc_input_three, tc_output_three = request.POST['test-input-three'].strip(), request.POST['test-output-three'].strip()

        # question_test_cases = request.POST['question-test-case']
        # if question_test_cases != '':
        #     question_tc_list = question_test_cases.split('\n')
        # else:
        #     question_tc_list = []

        tc_question_obj = TeacherQuestion.objects.create(
            question_name = question_name, 
            question_text = question_text,
            teacher_obj = teacher_obj
        )
        tc_question_obj.save()

        if tc_input_one != '':
            tq_tc_obj = TeacherQuestionTestCase.objects.create(
                teacher_question_obj = tc_question_obj,
                input_param = tc_input_one,
                correct_output = tc_output_one
            )
            tq_tc_obj.save()
        
        if tc_input_two != '':
            tq_tc_obj = TeacherQuestionTestCase.objects.create(
                teacher_question_obj = tc_question_obj,
                input_param = tc_input_two,
                correct_output = tc_output_two
            )
            tq_tc_obj.save()

        if tc_input_three != '':
            tq_tc_obj = TeacherQuestionTestCase.objects.create(
                teacher_question_obj = tc_question_obj,
                input_param = tc_input_three,
                correct_output = tc_output_three
            )
            tq_tc_obj.save()
        
        # for qtc in question_tc_list:
        #     qtc_list = qtc.split(' ;; ')
        #     qtc_input = qtc_list[0].strip()
        #     qtc_output = qtc_list[1].strip()
        #     tq_tc_obj = TeacherQuestionTestCase.objects.create(
        #         teacher_question_obj = tc_question_obj,
        #         input_param = qtc_input,
        #         correct_output = qtc_output
        #     )
        #     tq_tc_obj.save()
        
        return redirect('teacher_admin_question_management')

    
    tq_objects = TeacherQuestion.objects.filter(
        teacher_obj = teacher_obj
    ).order_by('-created_at')

    # TODO: get num_code_files for each question
    full_questions_list = []
    for tq_obj in tq_objects:
        num_pg_code_files = StudentPlaygroundCode.objects.filter(
            teacher_question_obj = tq_obj
        ).count()
        full_questions_list.append([
            tq_obj, num_pg_code_files
        ])

    return render(request, 'teacher_admin_question_management.html', {
        'teacher_obj': teacher_obj,
        'teacher_questions': full_questions_list
    })



# TODO: authorize the functions below


def teacher_question_delete(request):
    if request.method == "POST":
        if request.session.get("teacher_object", None) is None:
            return JsonResponse({'success': False, 'message': 'User not authorized.'})

        data = request.POST
        TeacherQuestion.objects.filter(id = data['qid']).delete()
        return JsonResponse({'success': True})



def teacher_student_delete(request):
    if request.method == "POST":
        if request.session.get("teacher_object", None) is None:
            return JsonResponse({'success': False, 'message': 'User not authorized.'})
        
        data = request.POST
        tsi_objects = TeacherStudentInvite.objects.filter(id = data['qid'])
        if len(tsi_objects) == 0:
            return JsonResponse({'success': False, 'message': 'Student not found.'})
        else:
            tsi_obj = tsi_objects[0]
            if tsi_obj.student_registered:
                TeacherStudentInvite.objects.filter(id = data['qid']).delete()
                Student.objects.filter(email = tsi_obj.student_email).delete()
            else:
                TeacherStudentInvite.objects.filter(id = data['qid']).delete()

        return JsonResponse({'success': True})



def teacher_admin_assistant_chat(request):
    if request.session.get("teacher_object", None) is None:
        # TODO: redirect to landing for now as private-beta for improving teacher-db-functionality
        return redirect('landing')

    teacher_obj = request.session.get("teacher_object")
    teacher_obj = Teacher.objects.get(id = teacher_obj['id'])

    general_teacher_assistant_cv_objects = TeacherConversation.objects.filter(
        teacher_obj = teacher_obj
    )

    return render(request, 'teacher_admin_assistant_chat.html', {
        'teacher_obj': teacher_obj,
        'teacher_assistant_conversations': general_teacher_assistant_cv_objects
    })



def teacher_admin_student_view(request, uid):
    
    if request.session.get("teacher_object", None) is None:
        # TODO: redirect to landing for now as private-beta for improving teacher-db-functionality
        return redirect('landing')

    teacher_obj = request.session.get("teacher_object")
    teacher_obj = Teacher.objects.get(id = teacher_obj['id'])

    print('student-id:', uid)
    student_obj = get_object_or_404(Student, id = uid)

    student_code_objects = StudentPlaygroundCode.objects.filter(
        student_obj = student_obj
    )

    final_student_code_rv = []
    for cd_obj in student_code_objects:
        code_conversation_objects = StudentPlaygroundConversation.objects.filter(
            code_obj = cd_obj
        )
        
        final_student_code_rv.append([
            cd_obj, code_conversation_objects
        ])


    return render(request, 'teacher_admin_student_view.html', {
        'teacher_obj': teacher_obj,
        'student_obj': student_obj,
        'student_code_objects': final_student_code_rv
    })



def student_admin_account_create(request):

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

            # duplicate student email check
            student_objects = Student.objects.filter(
                email = student_email
            )
            if len(student_objects) > 0:
                # return JsonResponse({'success': False, 'message': 'Student Account already exists.'})
                user_errors = {
                    'error_message': 'Student Account already exists.',
                    'form_type': 'account_create_form'
                }
                return render(request, 'student_admin_account_create.html', user_errors)

            f = forms.EmailField()
            try:
                student_email = f.clean(student_email)
            except:
                user_errors = {
                    'error_message': 'invalid email',
                    'form_type': 'account_create_form'
                }
                return render(request, 'student_admin_account_create.html', user_errors)

            
            if student_password != student_password_two:
                user_errors = {
                    'error_message': "passwords don't match",
                    'form_type': 'account_create_form'
                }
                return render(request, 'student_admin_account_create.html', user_errors)


            tsi_obj = TeacherStudentInvite.objects.get(student_email = student_email)
            hashed_pwd = make_password(student_password)

            sd_obj = Student.objects.create(
                full_name = student_full_name,
                teacher_obj = tsi_obj.teacher_obj,
                email = student_email, 
                password = hashed_pwd
            )
            sd_obj.save()

            # indicate that the student is registered
            tsi_obj.student_registered = True
            tsi_obj.save()

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


    student_obj_session = request.session['student_object']
    student_obj = Student.objects.get(id = student_obj_session['id'])
    student_questions = TeacherQuestion.objects.filter(
        teacher_obj = student_obj.teacher_obj
    ).order_by('-created_at')

    final_question_rv = []
    for std_q in student_questions:
        std_q_code_objects = StudentPlaygroundCode.objects.filter(
            teacher_question_obj = std_q,
            student_obj = student_obj
        )
        if len(std_q_code_objects) > 0:
            final_question_rv.append([
                std_q, std_q_code_objects[0]
            ])
        else:
            final_question_rv.append([
                std_q
            ])

    
    stud_general_tutor_conversations = StudentConversation.objects.filter(
        student_obj = student_obj
    )

    return render(request, 'student_admin_dashboard.html', {
        'student_obj': student_obj,
        'student_questions': final_question_rv,
        'stud_general_tutor_conversations': stud_general_tutor_conversations
    })



def student_tutor_handle_message(request):

    if request.session.get("student_object", None) is None:
        return redirect('student_admin_login')

    if request.method == 'POST':
        
        if request.session.get("student_object", None) is None:
            return JsonResponse({'success': False, 'message': 'No Authorized.'})

        student_obj_session = request.session['student_object']
        student_obj = Student.objects.get(id = student_obj_session['id'])
        
        user_question = request.POST['message'].strip()
        std_conversation_objects = StudentConversation.objects.filter(
            student_obj = student_obj
        ).order_by('-created_at')

        prev_conversation_st = ''
        if len(std_conversation_objects) > 0:
            prev_conversation_history = []
            for uc_tut_obj in std_conversation_objects[:3]:
                uc_question = uc_tut_obj.question
                uc_response = uc_tut_obj.response
                prev_conversation_history.append(f"Question: { uc_question }")
                prev_conversation_history.append(f"Response: { uc_response }")

            prev_conversation_st = '\n'.join(prev_conversation_history).strip()
        

        model_response_dict = main_utils.general_tutor_handle_question(
            question = user_question,
            previous_chat_history_st = prev_conversation_st
        )

        std_t_obj = StudentConversation.objects.create(
            student_obj = student_obj,
            question = model_response_dict['question'],
            question_prompt = model_response_dict['q_prompt'],
            response = model_response_dict['response'],
        )
        std_t_obj.save()
        
        return JsonResponse({'success': True, 'response': model_response_dict})



def teacher_assistant_handle_message(request):
     
    if request.session.get("teacher_object", None) is None:
        return redirect('teacher_admin_login')

    if request.method == 'POST':
        
        if request.session.get("teacher_object", None) is None:
            return JsonResponse({'success': False, 'message': 'No Authorized.'})

        teacher_obj = request.session.get("teacher_object")
        teacher_obj = Teacher.objects.get(id = teacher_obj['id'])

        user_question = request.POST['message'].strip()
        thr_conversation_objects = TeacherConversation.objects.filter(
            teacher_obj = teacher_obj
        ).order_by('-created_at')

        prev_conversation_st = ''
        if len(thr_conversation_objects) > 0:
            prev_conversation_history = []
            for uc_tut_obj in thr_conversation_objects[:3]:
                uc_question = uc_tut_obj.question
                uc_response = uc_tut_obj.response
                prev_conversation_history.append(f"Question: { uc_question }")
                prev_conversation_history.append(f"Response: { uc_response }")

            prev_conversation_st = '\n'.join(prev_conversation_history).strip()
        

        model_response_dict = main_utils.teacher_question_response(
            question = user_question,
            previous_chat_history_st = prev_conversation_st
        )

        tct_obj = TeacherConversation.objects.create(
            teacher_obj = teacher_obj,
            question = model_response_dict['question'],
            question_prompt = model_response_dict['q_prompt'],
            response = model_response_dict['response'],   
        )
        tct_obj.save()

        return JsonResponse({'success': True, 'response': model_response_dict})



def student_admin_playground(request):

    student_assigned_qid = request.GET.get('stdqid', None)
    student_playground_code_id = request.GET.get('stcid', None)

    teacher_obj = None
    if request.session.get("teacher_object", None) is not None:
        teacher_obj = request.session.get("teacher_object")
        teacher_obj = Teacher.objects.get(id = teacher_obj['id'])

    elif request.session.get("student_object", None) is None:
        return redirect('student_admin_login')

    # student_obj = None
    # teacher_obj = None
    # if request.session.get("teacher_object", None) is not None:
    #     teacher_obj = request.session.get("teacher_object")
    #     teacher_obj = Teacher.objects.get(id = teacher_obj['id'])

    # elif request.session.get("student_object", None) is None:
    #     return redirect('student_admin_login')

    # if teacher_obj is not None and student_playground_code_id is not None:
    #     std_code_obj = get_object_or_404(StudentPlaygroundCode, id = student_playground_code_id)
    #     student_code_conversations = []
    #     student_code_conversations = StudentPlaygroundConversation.objects.filter(
    #         code_obj = std_code_obj
    #     )

    #     tq_obj = None
    #     tq_obj_test_case_examples = []
    #     if student_assigned_qid is not None:
    #         tq_obj = get_object_or_404(TeacherQuestion, id = student_assigned_qid)
    #         tq_obj_test_case_examples = TeacherQuestionTestCase.objects.filter(teacher_question_obj = tq_obj)

    # else:
    #     student_obj_session = request.session['student_object']
    #     student_obj = Student.objects.get(id = student_obj_session['id'])

    #     tq_obj = None
    #     tq_obj_test_case_examples = []
    #     if student_assigned_qid is not None:
    #         tq_obj = get_object_or_404(TeacherQuestion, id = student_assigned_qid)
    #         tq_obj_test_case_examples = TeacherQuestionTestCase.objects.filter(teacher_question_obj = tq_obj)

    #     std_code_obj = None
    #     if student_playground_code_id is not None:
    #         std_code_obj = get_object_or_404(StudentPlaygroundCode, id = student_playground_code_id)

    #     student_code_conversations = []
    #     if std_code_obj is not None:
    #         student_code_conversations = StudentPlaygroundConversation.objects.filter(
    #             code_obj = std_code_obj
    #         )
    

    # student_obj = None
    # if teacher_obj is not None:
    #     student_obj = std_code_obj.student_obj
    # else:
    #     student_obj_session = request.session['student_object']
    #     student_obj = Student.objects.get(id = student_obj_session['id'])


    student_obj = None
    std_code_obj = None
    if student_playground_code_id is not None:

        if teacher_obj is not None:
            std_code_objects = StudentPlaygroundCode.objects.filter(
                id = student_playground_code_id
            )
            if len(std_code_objects) > 0:
                std_code_obj = std_code_objects[0]
                student_obj = std_code_obj.student_obj
            else:
                return redirect('teacher_admin_dashboard')
        
        else:
            student_obj_session = request.session['student_object']
            student_obj = Student.objects.get(id = student_obj_session['id'])
            
            std_code_objects = StudentPlaygroundCode.objects.filter(
                id = student_playground_code_id,
                student_obj = student_obj
            )
            if len(std_code_objects) > 0:
                std_code_obj = std_code_objects[0]
            else:
                return redirect('student_admin_dashboard')

    else:  # still can be valid student but didn't initialize the code yet
        student_obj_session = request.session['student_object']
        student_obj = Student.objects.get(id = student_obj_session['id'])

    tq_obj = None
    tq_obj_test_case_examples = []
    if student_assigned_qid is not None:

        tq_objects = TeacherQuestion.objects.filter(
            id = student_assigned_qid,
        )
        if len(tq_objects) == 0:
            if teacher_obj is not None:
                return redirect('teacher_admin_dashboard')
            else:
                return redirect('student_admin_dashboard')
        else:
            if teacher_obj is not None:
                tq_obj = tq_objects[0]
                tq_obj_test_case_examples = TeacherQuestionTestCase.objects.filter(teacher_question_obj = tq_obj)
            else:
                if student_obj is None:
                    return redirect('student_admin_dashboard')
                else:                    
                    tq_obj = tq_objects[0]
                    teacher_obj_for_question = tq_obj.teacher_obj
                    if student_obj.teacher_obj != teacher_obj_for_question:
                        return redirect('student_admin_dashboard')

                    tq_obj_test_case_examples = TeacherQuestionTestCase.objects.filter(teacher_question_obj = tq_obj)
    

    if std_code_obj is not None and tq_obj is not None:
        if std_code_obj.teacher_question_obj != tq_obj:
            return redirect('student_admin_dashboard')
  
    student_code_conversations = []
    if std_code_obj is not None:
        student_code_conversations = StudentPlaygroundConversation.objects.filter(
            code_obj = std_code_obj
        ).order_by('created_at')

    return render(request, 'student_playground_environment.html', {
        'teacher_obj': teacher_obj,
        'student_obj': student_obj,
        'student_playground_code_id': student_playground_code_id,
        'std_code_obj': std_code_obj,
        'stdqid': student_assigned_qid,
        'teacher_question_object': tq_obj,
        'teacher_question_test_cases': tq_obj_test_case_examples,
        'student_code_conversations': student_code_conversations
    })



def handle_student_playground_message(request):
    
    if request.method == 'POST':

        # print('form-data:', request.POST)

        user_code = request.POST['user_code']
        user_question = request.POST['message'].strip()
        user_stdqid = request.POST['stdqid']
        student_code_id_value = request.POST['student_code_id_value']

        initial_student_object = request.session.get("student_object", None)
        if initial_student_object is None:
            return JsonResponse({'success': False, 'message': 'user is not authenticated.'})

        student_obj = Student.objects.get(id = initial_student_object['id'])

        # TODO: add filter condition here
        st_question_obj = TeacherQuestion.objects.get(id = user_stdqid)

        spc_obj = None
        if student_code_id_value == 'None':  # code is not saved
            spc_obj = StudentPlaygroundCode.objects.create(
                student_obj = student_obj,
                teacher_question_obj = st_question_obj,
                user_code = user_code
            )
            spc_obj.save()

        else:
            spc_obj = StudentPlaygroundCode.objects.get(id = student_code_id_value, student_obj = student_obj)
        

        prev_conversation_history = []
        prev_conversation_messages = StudentPlaygroundConversation.objects.filter(
            student_obj = student_obj,
            code_obj = spc_obj
        ).order_by('-created_at')

        if len(prev_conversation_messages) > 0:
            for uc_obj in prev_conversation_messages[:3]:
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
        print('model-response:', model_response_dict)

        
        if student_code_id_value == 'None':

            st_pg_conv_obj = StudentPlaygroundConversation.objects.create(
                student_obj = student_obj,
                code_obj = spc_obj,
                question = model_response_dict['question'],
                question_prompt = model_response_dict['q_prompt'],
                response = model_response_dict['response'],
            )
            st_pg_conv_obj.save()

        else:

            spc_obj.user_code = user_code
            spc_obj.save()

            st_pg_conv_obj = StudentPlaygroundConversation.objects.create(
                student_obj = student_obj,
                code_obj = spc_obj,
                question = model_response_dict['question'],
                question_prompt = model_response_dict['q_prompt'],
                response = model_response_dict['response'],
            )
            st_pg_conv_obj.save()

    
        model_response_dict['cid'] = spc_obj.id
        return JsonResponse({'success': True, 'response': model_response_dict})



def save_student_playground_code(request):
    
    if request.method == 'POST':

        initial_student_object = request.session.get("student_object", None)
        if initial_student_object is None:
            return JsonResponse({'success': False, 'message': 'user is not authenticated.'})

        student_obj = Student.objects.get(id = initial_student_object['id'])


        print('POST-DATA:', request.POST)

        user_code = request.POST['user_code'].strip()
        stdqid = request.POST['stdqid']
        student_code_id_value = request.POST['student_code_id_value']

        # TODO: add filter condition here just in case stdqid object doesns't exist
        st_question_obj = TeacherQuestion.objects.get(id = stdqid)

        spc_obj = None
        if student_code_id_value == 'None':  # code is not saved
            spc_obj = StudentPlaygroundCode.objects.create(
                student_obj = student_obj,
                teacher_question_obj = st_question_obj,
                user_code = user_code
            )
            spc_obj.save()
            
            return JsonResponse({'success': True, 'cid': spc_obj.id})

        else:
            spc_obj = StudentPlaygroundCode.objects.get(id = student_code_id_value, student_obj = student_obj)
            spc_obj.user_code = user_code
            spc_obj.save()
    
            return JsonResponse({'success': True, 'cid': spc_obj.id})



def teacher_specific_question_view(request, qid):

    if request.session.get("teacher_object", None) is None:
        return redirect('landing')

    teacher_obj = request.session.get("teacher_object")
    teacher_obj = Teacher.objects.get(id = teacher_obj['id'])

    tq_objects = TeacherQuestion.objects.filter(
        id = qid,
        teacher_obj = teacher_obj
    )
    if len(tq_objects) == 0:
        return JsonResponse({'success': False, 'mesage': 'Question not found.'})

    tq_obj = tq_objects[0]

    student_code_files = StudentPlaygroundCode.objects.filter(
        teacher_question_obj = tq_obj
    )

    return render(request, 'teacher_specific_question_view.html', {
        'teacher_obj': teacher_obj,
        'question_obj': tq_obj,
        'student_code_files': student_code_files
    })



def landing_teacher_email_input(request):
    if request.method == 'POST':
        val = request.POST['teacher_email'].strip()
        lt_obj = LandingTeacherEmail.objects.create(
            email = val
        )
        lt_obj.save()

        return JsonResponse({'success': True})



### Super User Views - Experiment ###

def super_user_admin_dashboard(request):
    
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

        gt_conversation_count = UserGeneralTutorConversation.objects.filter(
            user_auth_obj = uobj
        ).count()

        final_all_users_rv.append({
            'user_obj': uobj,
            'user_created_at': datetime.datetime.fromtimestamp(float(uobj.created_at)),
            'user_last_login_in': datetime.datetime.fromtimestamp(float(uobj.updated_at)),
            'code_count': code_count,
            'conversation_count': conversation_count,
            'gt_conversation_count': gt_conversation_count
        })

    final_all_users_rv = sorted(final_all_users_rv, key=itemgetter('user_last_login_in'), reverse=True)

    requested_teacher_email_objects = LandingTeacherEmail.objects.all().order_by('-created_at')

    teacher_objects = Teacher.objects.all().order_by('-created_at')
    registered_teacher_student_list = []
    for tobj in teacher_objects:
        
        teacher_invited_students = TeacherStudentInvite.objects.filter(
            teacher_obj = tobj,
            student_registered = False
        ).count()
        teacher_actual_students = Student.objects.filter(
            teacher_obj = tobj
        ).count()

        registered_teacher_student_list.append({
            'teacher_obj': tobj,
            'teacher_invited_students_count': teacher_invited_students,
            'teacher_actual_students_count': teacher_actual_students
        })


    total_user_code_conversations = UserConversation.objects.all().count()
    total_user_code_files = UserCode.objects.all().count()
    total_user_general_conversations = UserGeneralTutorConversation.objects.all().count()

    return render(request, 'site_admin_dashboard.html', {
        'all_students': final_all_users_rv,
        'all_requested_teachers': requested_teacher_email_objects,
        'registered_teacher_student_list': registered_teacher_student_list,
        'total_user_code_conversations': total_user_code_conversations,
        'total_user_code_files': total_user_code_files,
        'total_user_general_conversations': total_user_general_conversations
    })



def super_user_admin_student_page(request, uid):
    
    if not request.user.is_superuser:
        return redirect('landing')

    user_auth_obj = get_object_or_404(UserOAuth, id = uid)

    final_user_rv = {}
    final_user_rv['user_obj'] = user_auth_obj
    final_user_rv['user_signup_date'] = datetime.datetime.fromtimestamp(float(user_auth_obj.created_at))
    final_user_rv['user_last_login_date'] = datetime.datetime.fromtimestamp(float(user_auth_obj.updated_at))
    
    user_code_objects = UserCode.objects.filter(
        user_auth_obj = user_auth_obj
    ).order_by('-created_at')

    final_code_rv = []
    for uc_obj in user_code_objects:
        user_conversation_objects = UserConversation.objects.filter(
            code_obj = uc_obj
        )
        final_code_rv.append([uc_obj, user_conversation_objects])

    # final_user_rv['user_code_objects'] = user_code_objects
    # final_user_rv['user_conversation_objects'] = user_conversation_objects

    user_gt_c_objects = UserGeneralTutorConversation.objects.filter(
        user_auth_obj = user_auth_obj
    ).order_by('-created_at')

    final_user_rv['user_code_objects'] = final_code_rv
    final_user_rv['user_gt_c_objects'] = user_gt_c_objects

    return render(request, 'site_admin_student_view.html', final_user_rv)



def super_user_motivation_prompt(request):
    # TODO: build, use, and go from there...
        # potentially building refactor-AI <-- literally a web-app at first (doesn't need to be vscode?)
    return render(request, 'super_user_motivation_prompt.html')




### Python New Course ###

def new_course_home(request):
    all_lesson_objects = PythonCourseLesson.objects.all()
    return render(request, 'course_home.html', {
        'all_lesson_objects': all_lesson_objects
    })


def new_course_lesson_page(request, lid):
    course_lesson_obj = get_object_or_404(PythonCourseLesson, id = lid)
    lesson_question_objects = PythonLessonQuestion.objects.filter(course_lesson_obj = course_lesson_obj)

    return render(request, 'course_lesson_page.html', {
        'course_lesson_object': course_lesson_obj,
        'lesson_question_objects': lesson_question_objects
    })


def new_course_playground(request):

    pcqid = request.GET.get('pcqid')

    initial_user_session = request.session.get("user")

    user_auth_obj = None    
    if initial_user_session is not None:
        user_oauth_objects = UserOAuth.objects.filter(email = initial_user_session['userinfo']['email'])
        if len(user_oauth_objects) > 0:
            user_auth_obj = user_oauth_objects[0]


    pc_question_obj = get_object_or_404(PythonLessonQuestion, id = pcqid)
    question_test_cases = PythonLessonQuestionTestCase.objects.filter(lesson_question_obj = pc_question_obj)

    user_code_obj = None
    
    user_code_objects = PythonLessonUserCode.objects.filter(
        lesson_question_obj = pc_question_obj,
        user_auth_obj = user_auth_obj
    )
    if len(user_code_objects) > 0:
        user_code_obj = user_code_objects[0]

    return render(request, 'course_playground_environment_new.html', {
        'user_session': initial_user_session,
        'pcqid': pcqid,
        'pc_question_obj': pc_question_obj,
        'pt_course_test_case_examples': question_test_cases,

        # 'code_id': user_code_obj.id,
        'user_code_obj': user_code_obj
    })


def new_course_handle_user_message(request):

    initial_user_session = request.session.get("user")

    if request.method == 'POST':

        user_question = request.POST['message'].strip()
        user_code = request.POST['user_code'].strip()     
        user_code = user_code.replace('`', '"').strip()

        initial_user_session = request.session.get('user')
        if initial_user_session is None:
            previous_message_st = request.POST['previous_messages'].strip()
            model_response_dict = main_utils.main_handle_question(
                question = user_question,
                student_code = user_code,
                previous_chat_history_st = previous_message_st
            )
            return JsonResponse({'success': True, 'response': model_response_dict})


        user_cid = request.POST['cid']
        user_pclid = request.POST['pclid']

        lesson_ques_obj = None
        if user_pclid != 'None':
            lesson_question_objects = PythonLessonQuestion.objects.filter(id = user_pclid)
            if len(lesson_question_objects) > 0:
                lesson_ques_obj = lesson_question_objects[0]


        user_oauth_obj = UserOAuth.objects.get(email = initial_user_session['userinfo']['email'])
        prev_conversation_history = []
        if user_cid != 'None':

            prev_conversation_messages = PythonLessonConversation.objects.filter(
                user_auth_obj = user_oauth_obj,
                code_obj_id = user_cid
            ).order_by('-created_at')

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
            rnd_code_filename = lesson_ques_obj.question_name

            uc_obj = PythonLessonUserCode.objects.create(
                user_auth_obj = user_oauth_obj,
                code_unique_name = rnd_code_filename,
                user_code = user_code,
                lesson_question_obj = lesson_ques_obj
            )
            uc_obj.save()
            
            ur_obj = PythonLessonConversation.objects.create(
                user_auth_obj = user_oauth_obj,
                code_obj = uc_obj,
                question = model_response_dict['question'],
                question_prompt = model_response_dict['q_prompt'],
                response = model_response_dict['response'],
            )
            ur_obj.save()

        else:
            uc_objects = PythonLessonUserCode.objects.filter(id = user_cid, user_auth_obj = user_oauth_obj)
            if len(uc_objects) == 0:
                return JsonResponse({'success': False, 'response': 'Object id not found.'})

            uc_obj = uc_objects[0]
            uc_obj.lesson_question_obj = lesson_ques_obj
            uc_obj.user_code = user_code
            uc_obj.save()

            ur_obj = PythonLessonConversation.objects.create(
                user_auth_obj = user_oauth_obj,
                code_obj = uc_obj,
                question = model_response_dict['question'],
                question_prompt = model_response_dict['q_prompt'],
                response = model_response_dict['response'],
            )
            ur_obj.save()

    
        model_response_dict['cid'] = uc_obj.id
        return JsonResponse({'success': True, 'response': model_response_dict})


def new_course_save_user_code(request):
    
    if request.method == 'POST':
        
        initial_user_session = request.session.get("user")

        if initial_user_session is not None:
            user_oauth_objects = UserOAuth.objects.filter(email = initial_user_session['userinfo']['email'])
            if len(user_oauth_objects) == 0:
                return JsonResponse({'success': False, 'response': 'User must be authenticated.'})            
        else:
            return JsonResponse({'success': False, 'response': 'User must be authenticated.'})

        user_auth_obj = user_oauth_objects[0]
        user_code = request.POST['user_code'].strip()
        user_code = user_code.replace('`', '"').strip()
        cid = request.POST['cid']
        lq_id = request.POST['pclid']

        print('user-cid:', cid)

        lesson_ques_obj = PythonLessonQuestion.objects.get(id = lq_id)

        if cid == 'None':

            rnd_code_filename = lesson_ques_obj.question_name

            uc_obj = PythonLessonUserCode.objects.create(
                user_auth_obj = user_auth_obj,
                code_unique_name = rnd_code_filename,
                user_code = user_code,
                lesson_question_obj = lesson_ques_obj
            )
            uc_obj.save()
            
            return JsonResponse({'success': True, 'cid': uc_obj.id})

        else:
            uc_objects = PythonLessonUserCode.objects.filter(
                id = cid, 
                user_auth_obj = user_auth_obj
            )
            if len(uc_objects) == 0:
                return JsonResponse({'success': False, 'response': 'Object id not found.'})

            uc_obj = uc_objects[0]
            uc_obj.lesson_question_obj = lesson_ques_obj
            uc_obj.user_code = user_code
            uc_obj.save()
            
            return JsonResponse({'success': True, 'cid': uc_obj.id})



### Python-Course-Admin ###

# def new_course_admin(request):
def new_course_admin_dashboard(request):
    user_is_admin = request.user.is_superuser
    if not user_is_admin:  # exempt from auth check; has visibility into all user's code
        return redirect('landing')
    
    return render(request, 'course_lesson_admin.html')


def new_course_admin_lesson_management(request):
    user_is_admin = request.user.is_superuser
    if not user_is_admin:  # exempt from auth check; has visibility into all user's code
        return redirect('landing')
    
    if request.method == 'POST':
        print('post:', request.POST)

        if not request.user.is_superuser:
            return JsonResponse({'success': False})

        if 'lesson-edit-value' in request.POST:
            lid = request.POST['lesson-id-value']
            pc_obj = PythonCourseLesson.objects.get(id = lid)
            pc_obj.lesson_title = request.POST['lesson-name'].strip()
            pc_obj.lesson_description = request.POST['lesson-text'].strip()
            pc_obj.lesson_video = request.POST['lesson-youtube-url'].strip()
            pc_obj.save()

        else:
            lesson_name = request.POST['lesson-name'].strip()
            lesson_description = request.POST['lesson-text'].strip()
            lesson_yt_url = request.POST['lesson-youtube-url'].strip()
            
            pc_lesson_obj = PythonCourseLesson.objects.create(
                lesson_title = lesson_name,
                lesson_description = lesson_description,
                lesson_video = lesson_yt_url
            )
            pc_lesson_obj.save()

        return redirect('new_course_admin_lesson_management')


    if 'lesson-edit-id' in request.GET:
        if not request.user.is_superuser:
            return JsonResponse({'success': False})

        lesson_edit_id = request.GET.get('lesson-edit-id')
        course_lessons = PythonCourseLesson.objects.all().order_by('order_number')
        return render(request, 'course_lesson_crud.html', {
            'course_lessons': course_lessons,
            'current_lesson_obj': PythonCourseLesson.objects.get(id = lesson_edit_id),
            'lesson_edit': True
        })

    course_lessons = PythonCourseLesson.objects.all().order_by('order_number')
    return render(request, 'course_lesson_crud.html', {
        'course_lessons': course_lessons
    })


import json
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def new_course_lesson_order_management(request):
    
    if request.method == 'POST':

        if not request.user.is_superuser:
            return JsonResponse({'success': False})

        d = json.loads(request.POST.get('data', ''))
        all_items = d['all_items']
        for obj_id in all_items:
            order_num = all_items[obj_id]
            cobj = PythonCourseLesson.objects.get(id = obj_id)
            cobj.order_number = order_num
            cobj.save()

        return JsonResponse({'success': True})


def new_course_lesson_delete(request):

    if request.method == 'POST':

        if not request.user.is_superuser:
            return JsonResponse({'success': False})

        PythonCourseLesson.objects.filter(id = request.POST['lid']).delete()
        return JsonResponse({'success': True})




def new_course_question_management(request):
    
    all_lesson_objects = PythonCourseLesson.objects.all()
    all_question_objects = PythonLessonQuestion.objects.all()

    if request.method == 'POST':
        question_name = request.POST['question-name'].strip()
        question_text = request.POST['question-text'].strip()
        lesson_obj_selected_id = request.POST['lesson_object_selected']

        tc_input_one, tc_output_one = request.POST['test-input-one'].strip(), request.POST['test-output-one'].strip()
        tc_input_two, tc_output_two = request.POST['test-input-two'].strip(), request.POST['test-output-two'].strip()
        tc_input_three, tc_output_three = request.POST['test-input-three'].strip(), request.POST['test-output-three'].strip()
        tc_input_four, tc_output_four = request.POST['test-input-four'].strip(), request.POST['test-output-four'].strip()
        tc_input_five, tc_output_five = request.POST['test-input-five'].strip(), request.POST['test-output-five'].strip()
        tc_input_six, tc_output_six = request.POST['test-input-six'].strip(), request.POST['test-output-six'].strip()

    
        course_lesson_obj = PythonCourseLesson.objects.get(id = lesson_obj_selected_id)
        
        tc_question_obj = PythonLessonQuestion.objects.create(
            question_name = question_name, 
            question_text = question_text,
            course_lesson_obj = course_lesson_obj
        )
        tc_question_obj.save()

        if tc_input_one != '' or tc_output_one != '':
            tq_tc_obj = PythonLessonQuestionTestCase.objects.create(
                lesson_question_obj = tc_question_obj,
                input_param = tc_input_one,
                correct_output = tc_output_one
            )
            tq_tc_obj.save()
        
        if tc_input_two != '' or tc_output_two != '':
            tq_tc_obj = PythonLessonQuestionTestCase.objects.create(
                lesson_question_obj = tc_question_obj,
                input_param = tc_input_two,
                correct_output = tc_output_two
            )
            tq_tc_obj.save()

        if tc_input_three != '' or tc_output_three != '':
            tq_tc_obj = PythonLessonQuestionTestCase.objects.create(
                lesson_question_obj = tc_question_obj,
                input_param = tc_input_three,
                correct_output = tc_output_three
            )
            tq_tc_obj.save()
        
        if tc_input_four != '' or tc_output_four != '':
            tq_tc_obj = PythonLessonQuestionTestCase.objects.create(
                lesson_question_obj = tc_question_obj,
                input_param = tc_input_four,
                correct_output = tc_output_four
            )
            tq_tc_obj.save()
        
        if tc_input_five != '' or tc_output_five != '':
            tq_tc_obj = PythonLessonQuestionTestCase.objects.create(
                lesson_question_obj = tc_question_obj,
                input_param = tc_input_five,
                correct_output = tc_output_five
            )
            tq_tc_obj.save()

        if tc_input_six != '' or tc_output_six != '':
            tq_tc_obj = PythonLessonQuestionTestCase.objects.create(
                lesson_question_obj = tc_question_obj,
                input_param = tc_input_six,
                correct_output = tc_output_six
            )
            tq_tc_obj.save()
        

    return render(request, 'course_question_management.html', {
        'all_lesson_objects': all_lesson_objects,
        'all_question_objects': all_question_objects
    })


def new_course_question_view(request, qid):
    question_obj = get_object_or_404(PythonLessonQuestion, id = qid)
    return render(request, 'course_question_view.html', {
        'question_object': question_obj
    })






import ast

def new_course_handle_solution_submit(request):

    if request.method == 'POST':

        user_code = request.POST['user_code'].strip()
        user_code = user_code.replace('`', '"').strip()
        user_cid = request.POST['cid']
        user_pclid = request.POST['pclid']
        user_message = request.POST['message'].strip()
        
        lesson_ques_obj = None
        if user_pclid != 'None':
            lesson_question_objects = PythonLessonQuestion.objects.filter(id = user_pclid)
            if len(lesson_question_objects) > 0:
                lesson_ques_obj = lesson_question_objects[0]


        pt_q_test_cases = PythonLessonQuestionTestCase.objects.filter(lesson_question_obj = lesson_ques_obj)
        test_case_correct_list = []
        for qtc_obj in pt_q_test_cases:
            tc_input = qtc_obj.input_param
            tc_output = qtc_obj.correct_output

            tc_input_list = ast.literal_eval(tc_input)

            valid_solution_dict = main_utils.course_question_solution_check(
                source_code = user_code,
                input_param = tc_input_list,
                output_param = tc_output,
            )

            valid_solution = valid_solution_dict['success']

            tc_status = 0
            if valid_solution:
                tc_status = 1

            test_case_correct_list.append({
                'tc_id_text': f'status_{ qtc_obj.id }',
                'status': tc_status,
                'message': valid_solution_dict['message']
            })


        print('Correct List:', test_case_correct_list)

        initial_user_session = request.session.get('user')
        if initial_user_session is None:
        
            # model_response_dict = main_utils.main_handle_question(
            #     question = user_message,
            #     student_code = user_code,
            #     previous_chat_history_st = ''
            # )
        
            model_response_dict = {
                'question': '',
                'q_prompt': '',
                'response': 'Lorem ipsum dolor sit amet, consectetur adipiscing elit.',
            }

            return JsonResponse({'success': True, 'response': model_response_dict, 'test_case_list': test_case_correct_list})

        else:

            user_oauth_obj = UserOAuth.objects.get(email = initial_user_session['userinfo']['email'])
        
            # model_response_dict = main_utils.main_handle_question(
            #     question = user_message,
            #     student_code = user_code,
            #     previous_chat_history_st = ''
            # )

            model_response_dict = {
                'question': '',
                'q_prompt': '',
                'response': 'Lorem ipsum dolor sit amet, consectetur adipiscing elit.',
            }

            if user_cid == 'None':

                rnd_code_filename = lesson_ques_obj.question_name

                uc_obj = PythonLessonUserCode.objects.create(
                    user_auth_obj = user_oauth_obj,
                    code_unique_name = rnd_code_filename,
                    user_code = user_code,
                    lesson_question_obj = lesson_ques_obj
                )
                uc_obj.save()

                return JsonResponse({
                    'success': True, 
                    'cid': uc_obj.id, 
                    'response': model_response_dict, 
                    'test_case_list': test_case_correct_list
                })

            else:
                uc_objects = PythonLessonUserCode.objects.filter(
                    id = user_cid, 
                    user_auth_obj = user_oauth_obj
                )
                if len(uc_objects) == 0:
                    return JsonResponse({'success': False, 'response': 'Object id not found.'})

                uc_obj = uc_objects[0]
                uc_obj.lesson_question_obj = lesson_ques_obj
                uc_obj.user_code = user_code
                uc_obj.save()

                return JsonResponse({
                    'success': True, 
                    'cid': uc_obj.id, 
                    'response': model_response_dict, 
                    'test_case_list': test_case_correct_list
                })
                





## REST API Views ##

@csrf_exempt
def test_api_response(request):
    
    print(request)

    post_data = json.loads(request.body.decode("utf-8"))
    print('post-data:', post_data)

    user_question = post_data['user_question'].strip()
    user_code = post_data['user_code'].strip()

    tutor_response = main_utils.main_handle_question(
        question = user_question, 
        student_code = user_code,
        previous_chat_history_st = ''
    )

    di = {
        'input': 'example',
        'output': 3,
        'user': 'testing'
    }
    
    return JsonResponse(data=di)







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

