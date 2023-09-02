from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.http import JsonResponse
from urllib.parse import quote_plus, urlencode

import os
import time
import functools
import secrets
import string
from dotenv import load_dotenv, find_dotenv
from authlib.integrations.django_client import OAuth

from .models import *
from . import main_utils




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
    print('cid:', code_id)

    qid = request.GET.get('qid', None)
    print('qid:', qid)

    if qid is not None:
        ls_q_obj = get_object_or_404(LessonQuestion, id = qid)

    uc_objects = UserCode.objects.filter(id = code_id)
    user_conversation_objects = []
    if len(uc_objects) > 0:
        uc_obj = uc_objects[0]
        user_conversation_objects = UserConversation.objects.filter(code_obj = uc_obj)
        # if len(us_conv_objects) > 0:
        #     user_conversation_obj = us_conv_objects[0]
    else:
        uc_obj = None
    
    return render(request, 'playground.html', {
        'user_session': initial_user_session,
        'code_id': code_id,
        'uc_obj': uc_obj,
        'user_conversation_objects': user_conversation_objects,
        'qid': qid,
        'lesson_question_object': ls_q_obj
    })


def lesson_dashboard(request):
    lesson_objects = Lesson.objects.all()
    return render(request, 'lesson_dashboard.html', {
        'lesson_objects': lesson_objects
    })


def questions(request, lid):
    
    lesson_obj = get_object_or_404(Lesson, id = lid)
    lesson_questions = LessonQuestion.objects.filter(
        lesson_obj = lesson_obj
    )

    return render(request, 'questions.html', {
        'lesson_object': lesson_obj,
        'lesson_questions': lesson_questions
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

        print('User-CID:', user_cid)

        user_oauth_obj = None
        prev_conversation_history = []
        if initial_user_session is not None:
            user_oauth_obj = UserOAuth.objects.get(email = initial_user_session['userinfo']['email'])
            print('user-auth-obj:', user_oauth_obj)
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
            rnd_code_filename = ''.join([secrets.choice(string.ascii_lowercase) for idx in range(10)])

            uc_obj = UserCode.objects.create(
                user_auth_obj = user_oauth_obj,
                code_unique_name = rnd_code_filename,
                user_code = user_code
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

        # print('form-data:', request.POST)

        # print('cid', request.POST['cid'], request.POST['cid'] == None, request.POST['cid'] == 'None')

        if initial_user_session is not None:
            user_oauth_objects = UserOAuth.objects.filter(email = initial_user_session['userinfo']['email'])
            if len(user_oauth_objects) == 0:
                return JsonResponse({'success': False, 'response': 'User must be authenticated.'})
        else:
            return JsonResponse({'success': False, 'response': 'User must be authenticated.'})

        user_auth_obj = user_oauth_objects[0]
        user_code = request.POST['user_code'].strip()
        cid = request.POST['cid']
        if cid == 'None':
            rnd_code_filename = ''.join([secrets.choice(string.ascii_lowercase) for idx in range(10)])
            uc_obj = UserCode.objects.create(
                user_auth_obj = user_auth_obj,
                code_unique_name = rnd_code_filename,
                user_code = user_code
            )
            uc_obj.save()
            return JsonResponse({'success': True, 'cid': uc_obj.id})

        else:
            # uc_obj = UserCode.objects.get(id = cid)
            uc_objects = UserCode.objects.filter(id = cid, user_auth_obj = user_auth_obj)
            if len(uc_objects) == 0:
                return JsonResponse({'success': False, 'response': 'Object id not found.'})
            
            uc_obj = uc_objects[0]
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

        uc_obj = UserCode.objects.get(
            id = cid,
            user_auth_obj = user_auth_obj
        )

        uc_obj.code_unique_name = new_file_name
        uc_obj.save()

        return JsonResponse({'success': True, 'cid': uc_obj.id, 'new_file_name': new_file_name})



