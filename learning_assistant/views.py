from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.http import JsonResponse
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
from .scripts.personal_course_gen import a_student_description_generation, b_student_course_outline_generation_new


if 'PRODUCTION' not in os.environ:
    dot_env_file = find_dotenv()
    load_dotenv(dot_env_file)
    

globals_dict = {}
globals_dict.update(
    __builtins__={
        'True': True,
        'False': False,
        'None': None,
        'str': str,
        'bool': bool,
        'int': int,
        'float': float,
        'enumerate': enumerate,
        'dict': dict,
        'list': list,
        'tuple': tuple,
        'map': map,
        'abs': abs,
        'min': min,
        'max': max,
        'sum': sum,
        'filter': filter,
        'round': round,
        'len': len,
        'repr': repr,
        'set': set,
        'all': all,
        'any': any,
        'ord': ord,
        'chr': chr,
        'divmod': divmod,
        'isinstance': isinstance,
        'range': range,
        'zip': zip,
        'sorted': sorted,
        'reversed': reversed
    }
)


import ast
import time
from wrapt_timeout_decorator import *

# @timeout_decorator.timeout(20, use_signals=False)
@timeout(5)
def new_question_solution_check(source_code, input_param, output_param, mode="exec"):
    source_code = source_code.strip()

    try:
        tree = ast.parse(source_code, mode=mode)
        function = tree.body[0]
        num_inputs = len(function.args.args)
    except: 
        return {'success': False, 'message': 'Invalid Syntax. Code could not compile.', 'user_function_output': None}

    try:
        source_code = compile(tree, "<string>", mode)
        restricted_locals = {}
        exec(source_code, globals_dict, restricted_locals)
    except:
        return {'success': False, 'message': 'Code did not compile. Ensure no print or import statements are present in the code.', 'user_function_output': None}

    user_function = restricted_locals[function.name]

    if num_inputs != len(input_param):  # user incorrectly specified number of required inputs in their function
        return {'success': False, 'message': f'The number of the parameters in the function is not correct. The function should have {len(input_param)} params.', 'user_function_output': None}

    if num_inputs == 1:        
        try:
            function_output = user_function(input_param[0])
        except: # function execution error
            return {'success': False, 'message': 'Python compilation error. Ensure your function does not contain any special keywords such as imports or print statements.', 'user_function_output': None}

        if function_output == output_param:
            return {'success': True, 'message': 'Test case successfully passed.', 'user_function_output': function_output}
        else:
            return {'success': False, 'message': 'Function returned wrong output.', 'user_function_output': function_output}

    elif num_inputs == 2:
        try:
            function_output = user_function(input_param[0], input_param[1])
        except: # function likely named a special python keyword
            return {'success': False, 'message': 'Python compilation error. Ensure your function does not contain any special keywords such as imports or print statements.', 'user_function_output': None}
        
        if function_output == output_param:
            return {'success': True, 'message': 'Test case successfully passed.', 'user_function_output': function_output}
        else:
            return {'success': False, 'message': 'Function returned wrong output.', 'user_function_output': function_output}

    elif num_inputs == 3:
        try:
            function_output = user_function(input_param[0], input_param[1], input_param[2])
        except: # function likely named a special python keyword
            return {'success': False, 'message': 'Python compilation error. Ensure your function does not contain any special keywords such as imports or print statements.', 'user_function_output': None}
        
        if function_output == output_param:
            return {'success': True, 'message': 'Test case successfully passed.', 'user_function_output': function_output}
        else:
            return {'success': False, 'message': 'Function returned wrong output.', 'user_function_output': function_output}
    
    elif num_inputs == 4:
        try:
            function_output = user_function(input_param[0], input_param[1], input_param[2], input_param[3])
        except: # function likely named a special python keyword
            return {'success': False, 'message': 'Python compilation error. Ensure your function does not contain any special keywords such as imports or print statements.', 'user_function_output': None}
        
        if function_output == output_param:
            return {'success': True, 'message': 'Test case successfully passed.', 'user_function_output': function_output}
        else:
            return {'success': False, 'message': 'Function returned wrong output.', 'user_function_output': function_output}



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

    user_info = token['userinfo']
    user_email = user_info['email']
    user_auth_type = user_info['sub']
    user_email_verified = user_info['email_verified']
    user_name = user_info['name']
    updated_date_ts = user_info['iat']

    user_auth_objects = UserOAuth.objects.filter(email = user_email)
    if len(user_auth_objects) > 0:
        user_auth_obj = user_auth_objects[0]
        user_auth_obj.email_verified = user_email_verified
        user_auth_obj.auth_type = user_auth_type
        user_auth_obj.name = user_name
        user_auth_obj.updated_at = updated_date_ts
        user_auth_obj.save()
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

    return redirect(request.build_absolute_uri(reverse("dashboard")))


def login(request):
    return oauth.auth0.authorize_redirect(
        request, request.build_absolute_uri(reverse("callback"))
    )


def signup(request):
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
    # return render(request, 'landing.html',  {
    return render(request, 'landing_new_one.html',  {        
        'user_session': initial_user_session,
    })


def about(request):
    initial_user_session = request.session.get("user")
    return render(request, 'about.html', {
        'user_session': initial_user_session
    })


def blog(request):
    return render(request, 'blog.html')


def playground(request):
    initial_user_session = request.session.get("user")

    code_id = request.GET.get('cid', None)
    lqid = request.GET.get('lqid', None)
    
    pclid = request.GET.get('pclid', None)

    user_oauth_obj = None
    if initial_user_session is not None:
        user_oauth_obj = UserOAuth.objects.get(email = initial_user_session['userinfo']['email'])
        
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


    initial_rnd_file_name = ''.join([secrets.choice(string.ascii_lowercase) for idx in range(6)])

    current_user_email = None
    if initial_user_session is not None:
        current_user_email = initial_user_session['userinfo']['email']

    # return render(request, 'playground.html', {
    return render(request, 'new_playground.html', {    
        'user_session': initial_user_session,
        'current_user_email': current_user_email,
        'code_id': code_id,
        'uc_obj': uc_obj,
        'user_conversation_objects': user_conversation_objects,
        'qid': lqid,
        'initial_rnd_file_name': initial_rnd_file_name,
        # 'student_obj': student_obj

        'pclid': pclid,
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
    ).order_by('-updated_at')
    
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


    print(final_rv)

    pt_course_code_objects = PythonLessonUserCode.objects.filter(user_auth_obj = user_oauth_obj).order_by('-created_at')
    
    user_file_objects = UserFiles.objects.filter(
        user_auth_obj = user_oauth_obj
    ).order_by('-uploaded_at')
    # print(user_file_objects)

    # total_lesson_questions = PythonLessonQuestion.objects.count()
    total_lesson_questions = PythonLessonQuestion.objects.exclude(order_number = 1).count()

    # print(initial_user_session)
    current_user_email = initial_user_session['userinfo']['email']

    # return render(request, 'new_user_dashboard.html',  {
    return render(request, 'user_dashboard.html',  {
        'user_session': initial_user_session,
        'current_user_email': current_user_email,
        'user_code_list': final_rv,
        'user_file_objects': user_file_objects,
        'pt_course_code_objects': pt_course_code_objects,
        'total_lesson_questions': total_lesson_questions,
        # 'user_code_objects': user_code_objects
        # 'user_conversations': user_conversations
    })


def handle_user_message(request):

    initial_user_session = request.session.get("user")

    if request.method == 'POST':

        # print('form-data:', request.POST)

        existing_anon_user_id = request.POST['existing_anon_user_id'].strip()
        user_question = request.POST['message'].strip()
        user_code = request.POST['user_code'].strip()     
        user_code = user_code.replace('`', '"').strip()
        user_code_obj_id = request.POST['cid']

        # print('user-code-obj-id:', user_code_obj_id, user_code_obj_id == 'None', user_code_obj_id is None)

        uc_obj = None
        initial_user_session = request.session.get('user')

        if initial_user_session is None:

            if user_code_obj_id == 'None':
                rnd_code_filename = ''.join([secrets.choice(string.ascii_lowercase) for idx in range(10)])

                uc_obj = UserCode.objects.create(
                    user_auth_obj = None,
                    unique_anon_user_id = existing_anon_user_id,
                    lesson_question_obj = None,
                    code_unique_name = rnd_code_filename,
                    user_code = user_code,
                )
                uc_obj.save()

            else:
                user_code_objects = UserCode.objects.filter(id = user_code_obj_id)
                if len(user_code_objects) == 0:
                    return JsonResponse({'success': False, 'response': 'Could not find associated code object.'})
                else:
                    uc_obj = user_code_objects[0]

            previous_message_st = request.POST['previous_messages'].strip()
            model_response_dict = main_utils.main_handle_question(
                question = user_question,
                programming_problem = None,
                student_code = user_code,
                previous_chat_history_st = previous_message_st
            )

            ur_obj = UserConversation.objects.create(
                user_auth_obj = None,
                unique_anon_user_id = existing_anon_user_id,
                code_obj = uc_obj,
                question = model_response_dict['question'],
                question_prompt = model_response_dict['q_prompt'],
                response = model_response_dict['response'],
            )
            ur_obj.save()

            model_response_dict['cid'] = uc_obj.id
            model_response_dict['code_file_name'] = uc_obj.code_unique_name
            return JsonResponse({'success': True, 'response': model_response_dict})

        else:
            
            user_oauth_obj = UserOAuth.objects.get(email = initial_user_session['userinfo']['email'])

            prev_conversation_history = []
            if user_code_obj_id != 'None':

                prev_conversation_messages = UserConversation.objects.filter(
                    code_obj_id = user_code_obj_id,
                    user_auth_obj = user_oauth_obj
                ).order_by('-created_at')

                if len(prev_conversation_messages) > 0:
                    for uc_obj in prev_conversation_messages[:5]:  # TODO: arbitrary limit of last 5 messages 
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
                programming_problem = None,
                student_code = user_code,
                previous_chat_history_st = prev_conversation_st
            )
            # print('model-response:', model_response_dict)

            if user_code_obj_id == 'None':
                
                rnd_code_filename = ''.join([secrets.choice(string.ascii_lowercase) for idx in range(10)])

                uc_obj = UserCode.objects.create(
                    user_auth_obj = user_oauth_obj,
                    code_unique_name = rnd_code_filename,
                    user_code = user_code,
                    lesson_question_obj = None
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

                uc_objects = UserCode.objects.filter(id = user_code_obj_id, user_auth_obj = user_oauth_obj)
                if len(uc_objects) == 0:
                    return JsonResponse({'success': False, 'response': 'Object id not found.'})

                uc_obj = uc_objects[0]
                # uc_obj.lesson_question_obj = lesson_ques_obj
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
            model_response_dict['code_file_name'] = uc_obj.code_unique_name
            return JsonResponse({'success': True, 'response': model_response_dict})


def save_user_code(request):
    
    initial_user_session = request.session.get("user")

    if request.method == 'POST':

        print('save-user-code-POST:', request.POST)

        if initial_user_session is not None:
            user_oauth_objects = UserOAuth.objects.filter(email = initial_user_session['userinfo']['email'])
            user_auth_obj = user_oauth_objects[0]
        #     if len(user_oauth_objects) == 0:
        #         return JsonResponse({'success': False, 'response': 'User must be authenticated.'})
        else:
            user_auth_obj = None
            # return JsonResponse({'success': False, 'response': 'User must be authenticated.'})

        
        user_anon_unique_id = request.POST['existing_anon_user_id'].strip()
        user_code = request.POST['user_code'].strip()
        user_code = user_code.replace('`', '"').strip()
        cid = request.POST['cid']

        if cid == 'None':
            
            # if lq_id == 'None':
            #     rnd_code_filename = ''.join([secrets.choice(string.ascii_lowercase) for idx in range(10)])
            # else:
            #     rnd_code_filename = lesson_ques_obj.question_name

            rnd_code_filename = ''.join([secrets.choice(string.ascii_lowercase) for idx in range(10)])

            uc_obj = UserCode.objects.create(
                user_auth_obj = user_auth_obj,
                unique_anon_user_id = user_anon_unique_id,
                code_unique_name = rnd_code_filename,
                user_code = user_code,
                lesson_question_obj = None
            )
            uc_obj.save()
            return JsonResponse({'success': True, 'cid': uc_obj.id, 'code_file_name': uc_obj.code_unique_name})

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
        user_code = request.POST['user_code'].strip()
        user_code = user_code.replace('`', '"').strip()

        if cid == 'None':
            uc_obj = UserCode.objects.create(
                user_auth_obj = user_auth_obj,
                code_unique_name = new_file_name,
                user_code = user_code,
                lesson_question_obj = None
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


def general_cs_tutor(request):

    initial_user_session = request.session.get("user")
    tchid = request.GET.get('tchid', None)
    
    current_user_email = None
    if initial_user_session is not None:
        current_user_email = initial_user_session['userinfo']['email']

    user_oauth_obj = None
    if initial_user_session is not None:
        user_oauth_obj = UserOAuth.objects.get(email = initial_user_session['userinfo']['email'])
    
    user_full_conversation_list = []
    if user_oauth_obj is not None:
        parent_conv_objects = UserGeneralTutorParent.objects.filter(
            user_auth_obj = user_oauth_obj
        )
        cv_count = 1
        for pc_obj in parent_conv_objects:
            past_conv_messages = UserGeneralTutorConversation.objects.filter(
                user_auth_obj = user_oauth_obj,
                chat_parent_object = pc_obj
            )
            user_full_conversation_list.append([
                f"Conversation #{cv_count}",
                pc_obj,
                past_conv_messages
            ])
            cv_count += 1

    user_full_conversation_list = user_full_conversation_list[::-1]

    current_cid_parent_conv_obj = None
    current_cid_past_messages = []
    if tchid is not None:
        parent_conv_objects = UserGeneralTutorParent.objects.filter(
            user_auth_obj = user_oauth_obj,
            id = tchid
        )
        if len(parent_conv_objects) == 0:
            current_cid_parent_conv_obj = None
        else:
            current_cid_parent_conv_obj = parent_conv_objects[0]
            current_cid_past_messages = UserGeneralTutorConversation.objects.filter(
                user_auth_obj = user_oauth_obj,
                chat_parent_object = current_cid_parent_conv_obj
            )



    return render(request, 'new_general_cs_tutor_chat.html', {
        'user_session': initial_user_session,
        'current_user_email': current_user_email,
        'current_conversation_parent_object': current_cid_parent_conv_obj,
        'current_conversation_list': current_cid_past_messages,
        'all_user_conversation_list': user_full_conversation_list
    })


def handle_general_tutor_user_message(request):
    initial_user_session = request.session.get("user")

    if request.method == 'POST':
        print('cs-chat-data:', request.POST)

        user_anon_unique_id = request.POST['existing_anon_user_id'].strip()
        user_question = request.POST['message'].strip()
        general_cs_chat_parent_obj_id = request.POST['general_cs_chat_parent_obj_id']

        initial_user_session = request.session.get('user')

        ut_conv_parent_obj = None
        prev_conversation_st = ''
        user_oauth_obj = None
        if initial_user_session is None:
            user_oauth_obj = None
            prev_conversation_st = request.POST['prev_conversation_history_st']
            ut_conv_parent_obj = UserGeneralTutorParent.objects.create(
                unique_anon_user_id = user_anon_unique_id,
            )
            ut_conv_parent_obj.save()
        else:
            user_oauth_obj = UserOAuth.objects.get(email = initial_user_session['userinfo']['email'])

            if general_cs_chat_parent_obj_id == '':

                # TODO: Names will just be "Conversation {count}" on frontend
                ut_conv_parent_obj = UserGeneralTutorParent.objects.create(
                    user_auth_obj = user_oauth_obj,
                )
                ut_conv_parent_obj.save()

            else:
                ut_conv_parent_objects = UserGeneralTutorParent.objects.filter(id = general_cs_chat_parent_obj_id)
                if len(ut_conv_parent_objects) == 0:
                    return JsonResponse({'success': False, 'message': 'object not found.'})
                else:
                    ut_conv_parent_obj = ut_conv_parent_objects[0]

            ug_tut_cv_objects = UserGeneralTutorConversation.objects.filter(
                user_auth_obj = user_oauth_obj,
                chat_parent_object = ut_conv_parent_obj
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

        if user_oauth_obj is not None:  ## regardless of if signed in or anon

            # TODO: test and finalize to ensure this works
            uct_obj = UserGeneralTutorConversation.objects.create(
                user_auth_obj = user_oauth_obj,
                chat_parent_object = ut_conv_parent_obj,
                question = model_response_dict['question'],
                question_prompt = model_response_dict['q_prompt'],
                response = model_response_dict['response'],
            )
            uct_obj.save()
        
        else:
            uct_obj = UserGeneralTutorConversation.objects.create(
                unique_anon_user_id = user_anon_unique_id,
                chat_parent_object = ut_conv_parent_obj,
                question = model_response_dict['question'],
                question_prompt = model_response_dict['q_prompt'],
                response = model_response_dict['response'],
            )
            uct_obj.save()

        # model_response_dict['uct_parent_obj_id'] = ugt_parent_obj.id
        model_response_dict['uct_parent_obj_id'] = ut_conv_parent_obj.id
        return JsonResponse({'success': True, 'response': model_response_dict})



## Personal Course Gen - Views ##
def personal_course_gen_sb_chat(request):
    
    initial_user_session = request.session.get("user")
    pbg_id = request.GET.get('pgid', None)
    
    current_user_email = None
    if initial_user_session is not None:
        current_user_email = initial_user_session['userinfo']['email']

    user_oauth_obj = None
    if initial_user_session is not None:
        user_oauth_obj = UserOAuth.objects.get(email = initial_user_session['userinfo']['email'])

    student_background_full_conversation_list = []
    if user_oauth_obj is not None:
        parent_conv_objects = UserBackgroundParent.objects.filter(
            user_auth_obj = user_oauth_obj
        )
        cv_count = 1
        for pc_obj in parent_conv_objects:
            past_conv_messages = UserBackgroundConversation.objects.filter(
                user_auth_obj = user_oauth_obj,
                chat_parent_object = pc_obj
            )
            student_background_full_conversation_list.append([
                f"Conversation #{cv_count}",
                pc_obj,
                past_conv_messages
            ])
            cv_count += 1

    student_background_full_conversation_list = student_background_full_conversation_list[::-1]

    current_cid_parent_conv_obj = None
    current_cid_past_messages = []
    if pbg_id is not None:

        ub_parent_objects = UserBackgroundParent.objects.filter(
            user_auth_obj = user_oauth_obj,
            id = pbg_id
        )
        if len(ub_parent_objects) == 0:
            current_cid_parent_conv_obj = None
        else:
            current_cid_parent_conv_obj = ub_parent_objects[0]
            current_cid_past_messages = UserBackgroundConversation.objects.filter(
                user_auth_obj = user_oauth_obj,
                chat_parent_object = current_cid_parent_conv_obj
            )

    return render(request, 'personal_course_gen_sb_chat.html', {
        'user_session': initial_user_session,
        'current_user_email': current_user_email,
        'current_conversation_parent_object': current_cid_parent_conv_obj,
        'current_conversation_list': current_cid_past_messages,
        'all_user_conversation_list': student_background_full_conversation_list,
        'personal_course_student_background': True
    })



def handle_student_background_chat_message(request):
    initial_user_session = request.session.get("user")

    if request.method == 'POST':
        print('cs-chat-data:', request.POST)

        initial_user_session = request.session.get('user')
        user_question = request.POST['message'].strip()
        user_background_parent_obj_id = request.POST['user_background_parent_obj_id']

        if initial_user_session is None:
            return JsonResponse({'success': False, 'message': 'Not Authenticated.'})

        user_oauth_obj = UserOAuth.objects.get(email = initial_user_session['userinfo']['email'])
        prev_conversation_st = ''
        if user_background_parent_obj_id == '':
            ut_conv_parent_obj = UserBackgroundParent.objects.create(
                user_auth_obj = user_oauth_obj
            )
            ut_conv_parent_obj.save()
        else:
            ut_conv_parent_objects = UserBackgroundParent.objects.filter(
                id = user_background_parent_obj_id
            )
            if len(ut_conv_parent_objects) == 0:
                return JsonResponse({'success': False, 'message': 'object not found.'})
            else:
                ut_conv_parent_obj = ut_conv_parent_objects[0]

            ug_tut_cv_objects = UserBackgroundConversation.objects.filter(
                user_auth_obj = user_oauth_obj,
                chat_parent_object = ut_conv_parent_obj
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

        model_response_dict = a_student_description_generation.generate_answer(
            student_response = user_question,
            prev_chat_history = prev_conversation_st
        )

        model_response_json = model_response_dict['response']
        model_response_final_message = model_response_json['final_message']
        model_response_message_str = model_response_json['response'].strip()

        uct_obj = UserBackgroundConversation.objects.create(
            user_auth_obj = user_oauth_obj,
            chat_parent_object = ut_conv_parent_obj,
            question = model_response_dict['student_response'],
            question_prompt = model_response_dict['q_prompt'],
            response = model_response_dict['response'],
            model_response_is_final_message = model_response_final_message,
            model_response_text = model_response_message_str
        )
        uct_obj.save()

        if model_response_final_message is False:
            model_response_dict['uct_parent_obj_id'] = ut_conv_parent_obj.id
            return JsonResponse({'success': True, 'response': model_response_dict, 'final_message': False})

        else: # conversation is complete, redirect to course outline page
            ut_conv_parent_obj.final_response = model_response_message_str
            ut_conv_parent_obj.save()
            
            initial_student_course_outline_response_dict = b_student_course_outline_generation_new.generate_course_outline(
                student_response = '',
                student_info = model_response_message_str,
                student_course_outline = '',
                previous_student_chat_history = ''
            )

            initial_student_course_outline_response_json = initial_student_course_outline_response_dict['response']
            initial_student_course_name = initial_student_course_outline_response_json['name'].strip()
            initial_student_course_description = initial_student_course_outline_response_json['description'].strip()
            # initial_student_course_outline = initial_student_course_outline_response_json['outline'].strip()
            initial_student_course_modules_list = initial_student_course_outline_response_json['modules']
            # initial_student_course_modules_list = ast.literal_eval(initial_student_course_modules)
            print(f"Course Modules List: {initial_student_course_modules_list} | TYPE OF COURSE MODULES: {type(initial_student_course_modules_list)}")

            ucourse_obj = UserCourse.objects.create(
                initial_background_object = ut_conv_parent_obj,
                name = initial_student_course_name,
                description = initial_student_course_description,
                module_list = initial_student_course_modules_list
            )
            ucourse_obj.save()
            
            for module_dict in initial_student_course_modules_list:

                md_num = module_dict['module_number']
                md_topic = module_dict['module_topic']
                md_description = module_dict['module_description']
                print('md-desc:', md_description)
                # md_description_str = '\n'.join(md_description)

                md_obj = UserCourseModules.objects.create(
                    parent_course_object = ucourse_obj,
                    module_number = md_num,
                    module_topic = md_topic,
                    module_description = md_description,
                )
                md_obj.save()

            return JsonResponse({'success': True, 'response': model_response_dict, 'final_message': True, 'new_course_object_id': ucourse_obj.id})

            # # TODO: need to pass associated created course-id (along with doing regular auth checks on the course-outline-page)
            # return redirect('student_course_outline')
            

# TODO: fetch and display the relevant information (initially for testing , will just be one)
# def student_course_outline(request, cid):
def student_course_outline(request):
    # course_obj = get_object_or_404(UserCourse, cid)
    # all_course_objects = UserCourse.objects.all()
    # # course_object = all_course_objects[len(all_course_objects)-1]
    # course_object = all_course_objects[5]

    all_course_objects = UserCourse.objects.all().order_by('-created_at')
    course_object = all_course_objects[0]

    course_module_list = UserCourseModules.objects.filter(
        parent_course_object = course_object
    ).order_by('module_number')
    course_module_list_rv = []
    for md_obj in course_module_list:
        course_module_list_rv.append([md_obj, ast.literal_eval(md_obj.module_description)])

    course_user_conversation_objects = UserCourseOutlineConversation.objects.filter(
        course_parent_object = course_object
    )
    print(f"User Conversation Objects: {course_user_conversation_objects}")

    user_conversation_rv = []
    for cv_obj in course_user_conversation_objects:
        # print(cv_obj.response['message_to_student'])
        cv_di = ast.literal_eval(cv_obj.response)
        user_conversation_rv.append([cv_obj.question, cv_di['message_to_student']])
        # user_conversation_rv.append(cv_di['message_to_student'])

    return render(request, 'student_course_outline.html', {
        'course_object': course_object,
        'course_module_list': course_module_list_rv,
        'user_conversation_objects': user_conversation_rv
    })



def student_course_outline_handle_message(request):
    initial_user_session = request.session.get("user")

    if request.method == 'POST':
        print('cs-chat-data:', request.POST)

        initial_user_session = request.session.get('user')
        user_oauth_obj = UserOAuth.objects.get(email = initial_user_session['userinfo']['email'])
        parent_course_obj_id = request.POST['course_outline_object_id']
        user_message = request.POST['message'].strip()

        course_obj = UserCourse.objects.get(id = parent_course_obj_id)
        initial_student_background = course_obj.initial_background_object.final_response

        past_user_conversation_objects = UserCourseOutlineConversation.objects.filter(course_parent_object = course_obj)
        prev_conversation_history = []
        for uc_obj in past_user_conversation_objects[:3]:
            uc_question = uc_obj.question
            uc_response = uc_obj.response
            prev_conversation_history.append(f"Question: { uc_question }")
            prev_conversation_history.append(f"Response: { uc_response }")

        prev_conversation_st = '\n'.join(prev_conversation_history).strip()

        new_course_outline_model_response_dict = b_student_course_outline_generation_new.generate_course_outline(
            student_response = user_message,
            student_info = initial_student_background,
            student_course_outline = '',
            previous_student_chat_history = prev_conversation_st
        )
  
        new_student_course_outline_response_json = new_course_outline_model_response_dict['response']
        course_outline_generation = new_student_course_outline_response_json['outline_generation']
        
        print(f"JSON DATA: {new_student_course_outline_response_json}")
        print()
        print(f"COURSE OUTLINE GENERATION: {course_outline_generation}")

        if course_outline_generation:  # new/updated course outline
            updated_course_name = new_student_course_outline_response_json['name']
            updated_course_description = new_student_course_outline_response_json['description']
            updated_course_module_list = new_student_course_outline_response_json['modules']
            
            course_obj.name = updated_course_name
            course_obj.description = updated_course_description
            course_obj.module_list = updated_course_module_list
            course_obj.save()

            uc_outline_obj = UserCourseOutlineConversation.objects.create(
                user_auth_obj = user_oauth_obj,
                course_parent_object = course_obj,
                question = user_message,
                question_prompt = new_course_outline_model_response_dict['q_prompt'],
                response = new_course_outline_model_response_dict['response']
            )
            uc_outline_obj.save()
        
            UserCourseModules.objects.filter(parent_course_object = course_obj).delete()

            for module_dict in updated_course_module_list:
                md_num = module_dict['module_number']
                md_topic = module_dict['module_topic']
                md_description = module_dict['module_description']

                md_obj = UserCourseModules.objects.create(
                    parent_course_object = course_obj,
                    module_number = md_num,
                    module_topic = md_topic,
                    module_description = md_description,
                )
                md_obj.save()

        else:
            uc_outline_obj = UserCourseOutlineConversation.objects.create(
                user_auth_obj = user_oauth_obj,
                course_parent_object = course_obj,
                question = user_message,
                question_prompt = new_course_outline_model_response_dict['q_prompt'],
                response = new_course_outline_model_response_dict['response']
            )
            uc_outline_obj.save()


        return JsonResponse({
            'success': True, 
            'new_course_outline_generation': course_outline_generation,
            'response': new_course_outline_model_response_dict,
            'course_object_id': course_obj.id
        })

        # new_student_course_name = new_student_course_outline_response_json['name'].strip()
        # new_student_course_description = new_student_course_outline_response_json['description'].strip()
        # new_course_modules_list = new_student_course_outline_response_json['modules']

        # course_obj.name = new_student_course_name
        # course_obj.description = new_student_course_description
        # course_obj.outline = new_student_course_outline
        # course_obj.save()

        # initial_student_course_outline_response_dict = b_student_course_outline_generation_new.generate_course_outline(
        #     student_response = '',
        #     student_info = model_response_message_str,
        #     student_course_outline = '',
        #     previous_student_chat_history = ''
        # )

        # initial_student_course_outline_response_json = initial_student_course_outline_response_dict['response']
        # initial_student_course_name = initial_student_course_outline_response_json['name'].strip()
        # initial_student_course_description = initial_student_course_outline_response_json['description'].strip()
        # # initial_student_course_outline = initial_student_course_outline_response_json['outline'].strip()
        # initial_student_course_modules_list = initial_student_course_outline_response_json['modules']
        # # initial_student_course_modules_list = ast.literal_eval(initial_student_course_modules)
        # print(f"Course Modules List: {initial_student_course_modules_list} | TYPE OF COURSE MODULES: {type(initial_student_course_modules_list)}")

        # ucourse_obj = UserCourse.objects.create(
        #     initial_background_object = ut_conv_parent_obj,
        #     name = initial_student_course_name,
        #     description = initial_student_course_description,
        #     module_list = initial_student_course_modules_list
        # )
        # ucourse_obj.save()
        
        # for module_dict in initial_student_course_modules_list:

        #     md_topic = module_dict['module_topic']
        #     md_description = module_dict['module_description']
        #     print('md-desc:', md_description)
        #     # md_description_str = '\n'.join(md_description)

        #     md_obj = UserCourseModules.objects.create(
        #         parent_course_object = ucourse_obj,
        #         module_topic = md_topic,
        #         module_description = md_description,
        #     )
        #     md_obj.save()
  
        # new_student_course_outline_response_json = new_course_outline_model_response_dict['response']
        # new_student_course_name = new_student_course_outline_response_json['name'].strip()
        # new_student_course_description = new_student_course_outline_response_json['description'].strip()
        # new_student_course_outline = new_student_course_outline_response_json['outline'].strip()

        # course_obj.name = new_student_course_name
        # course_obj.description = new_student_course_description
        # course_obj.outline = new_student_course_outline
        # course_obj.save()

        # uc_outline_obj = UserCourseOutlineConversation.objects.create(
        #     user_auth_obj = user_oauth_obj,
        #     course_parent_object = course_obj,
        #     question = user_message,
        #     question_prompt = new_course_outline_model_response_dict['q_prompt'],
        #     response = new_course_outline_model_response_dict['response']
        # )
        # uc_outline_obj.save()

        # return JsonResponse({
        #     'success': True, 
        #     'response': new_course_outline_model_response_dict, 
        #     'course_object_id': course_obj.id
        # })



# TODO: 
def personal_course_homepage(request):

    all_course_objects = UserCourse.objects.all().order_by('-created_at')
    course_object = all_course_objects[0]

    course_module_list = UserCourseModules.objects.filter(
        parent_course_object = course_object
    ).order_by('module_number')
    course_module_list_rv = []
    for md_obj in course_module_list:
        course_module_list_rv.append([md_obj, ast.literal_eval(md_obj.module_description)])

    return render(request, 'new_course_homepage.html', {
        'course_object': course_object,
        'course_module_list': course_module_list_rv,
    })






### Super User Admin Dashboard - Views ###

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

    total_python_user_code_files = PythonLessonUserCode.objects.all().count()
    total_python_user_code_submissions = PythonLessonQuestionUserSubmission.objects.all().count()
    total_course_user_conversations = PythonLessonConversation.objects.all().count()
    new_landing_page_emails = LandingEmailSubscription.objects.all()

    return render(request, 'site_admin_dashboard.html', {
        'all_students': final_all_users_rv,
        'all_requested_teachers': requested_teacher_email_objects,
        'registered_teacher_student_list': registered_teacher_student_list,
        'total_user_code_conversations': total_user_code_conversations,
        'total_user_code_files': total_user_code_files,
        'total_user_general_conversations': total_user_general_conversations,

        'total_python_user_code_files': total_python_user_code_files,
        'total_python_user_code_submissions': total_python_user_code_submissions,
        'total_course_user_conversations': total_course_user_conversations,
        'new_landing_page_emails': new_landing_page_emails
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
    
    initial_user_session = request.session.get("user")
    user_auth_obj = None    
    if initial_user_session is not None:
        user_oauth_objects = UserOAuth.objects.filter(email = initial_user_session['userinfo']['email'])
        if len(user_oauth_objects) > 0:
            user_auth_obj = user_oauth_objects[0]
    
    all_lesson_objects = PythonCourseLesson.objects.all().order_by('order_number')

    # TODO: very inefficient approach; keep track of the progress at the lesson and user level <-- new model just for this
    rv = []
    user_question_complete_count = 0
    for lobj in all_lesson_objects:
        tmp_lesson_question_objects = PythonLessonQuestion.objects.filter(course_lesson_obj = lobj)
        num_questions = len(tmp_lesson_question_objects)

        user_lesson_complete = False
        user_lesson_progress = False
        user_lesson_not_started = False
        total_complete_count = 0
        if user_auth_obj is not None:

            for tlq_obj in tmp_lesson_question_objects:

                py_q_sub_objects = PythonLessonQuestionUserSubmission.objects.filter(
                    lesson_question_obj = tlq_obj, 
                    user_auth_obj = user_auth_obj
                )
                py_q_tmp_dict = {}
                for py_q_sub in py_q_sub_objects:
                    # lq_id = py_q_sub.id
                    lq_id = tlq_obj.id
                    lq_complete = py_q_sub.complete
                    if lq_id in py_q_tmp_dict:
                        tp_li = py_q_tmp_dict[lq_id]
                        tp_li.append(lq_complete)
                        py_q_tmp_dict[lq_id] = tp_li
                    else:
                        py_q_tmp_dict[lq_id] = [lq_complete]
                
                for qid in py_q_tmp_dict:
                    q_tmp_li = py_q_tmp_dict[qid]
                    if True in q_tmp_li:
                        total_complete_count += 1

                if total_complete_count == num_questions:
                    user_lesson_complete = True
                elif total_complete_count < num_questions and len(py_q_tmp_dict) > 0:
                    user_lesson_progress = True
                else:
                    user_lesson_not_started = True
        
        user_question_complete_count += total_complete_count

        if user_lesson_complete:
            rv.append([lobj, num_questions, 'complete', total_complete_count])
        elif user_lesson_progress:
            rv.append([lobj, num_questions, 'progress', total_complete_count])
        else:
            rv.append([lobj, num_questions, 'not_started', total_complete_count])


    return render(request, 'course_home.html', {
        'all_lesson_objects': rv,
        'total_lesson_questions': PythonLessonQuestion.objects.exclude(order_number = 1).count(),
        'user_completed_questions': user_question_complete_count,
        'user_session': initial_user_session,
    })


def new_course_lesson_page(request, lid):
    course_lesson_obj = get_object_or_404(PythonCourseLesson, id = lid)
    lesson_question_objects = PythonLessonQuestion.objects.filter(course_lesson_obj = course_lesson_obj)

    next_order_number = course_lesson_obj.order_number + 1
    prev_order_number = course_lesson_obj.order_number - 1
    next_lesson_obj = None
    if PythonCourseLesson.objects.filter(order_number = next_order_number).count() > 0:
        next_lesson_obj = PythonCourseLesson.objects.get(order_number = next_order_number)

    prev_lesson_obj = None
    if PythonCourseLesson.objects.filter(order_number = prev_order_number).count() > 0:
        prev_lesson_obj = PythonCourseLesson.objects.get(order_number = prev_order_number)

    initial_user_session = request.session.get("user")
    user_auth_obj = None    
    if initial_user_session is not None:
        user_oauth_objects = UserOAuth.objects.filter(email = initial_user_session['userinfo']['email'])
        if len(user_oauth_objects) > 0:
            user_auth_obj = user_oauth_objects[0]

    lq_rv = []
    for lq_obj in lesson_question_objects:
        if user_auth_obj is not None:
            lq_submission_objects = PythonLessonQuestionUserSubmission.objects.filter(lesson_question_obj = lq_obj, user_auth_obj = user_auth_obj)
            lq_complete = False
            for lq_sub_obj in lq_submission_objects:
                if lq_sub_obj.complete is True:
                    lq_complete = True
                    break
        else:
            lq_complete = False

        lq_rv.append([lq_obj, lq_complete])


    course_video_lesson_chat_list = []
    if user_auth_obj is not None:
        course_video_lesson_chat_list = PythonLessonVideoConversation.objects.filter(
            user_auth_obj = user_auth_obj,
            course_lesson_obj = course_lesson_obj
        )


    user_question_complete_count = 0
    # for lobj in all_lesson_objects:

    tmp_lesson_question_objects = PythonLessonQuestion.objects.filter(course_lesson_obj = course_lesson_obj)
    num_questions = len(tmp_lesson_question_objects)

    total_complete_count = 0
    if user_auth_obj is not None:

        for tlq_obj in tmp_lesson_question_objects:

            py_q_sub_objects = PythonLessonQuestionUserSubmission.objects.filter(
                lesson_question_obj = tlq_obj, 
                user_auth_obj = user_auth_obj
            )
            py_q_tmp_dict = {}
            for py_q_sub in py_q_sub_objects:
                lq_id = tlq_obj.id
                lq_complete = py_q_sub.complete
                if lq_id in py_q_tmp_dict:
                    tp_li = py_q_tmp_dict[lq_id]
                    tp_li.append(lq_complete)
                    py_q_tmp_dict[lq_id] = tp_li
                else:
                    py_q_tmp_dict[lq_id] = [lq_complete]
            
            for qid in py_q_tmp_dict:
                q_tmp_li = py_q_tmp_dict[qid]
                if True in q_tmp_li:
                    total_complete_count += 1

    
    return render(request, 'course_lesson_page.html', {
        'course_lesson_object': course_lesson_obj,
        'course_video_lesson_chat_list': course_video_lesson_chat_list,
        'lesson_question_objects': lesson_question_objects,
        'total_question_complete_count': total_complete_count,
        'next_lesson_obj': next_lesson_obj,
        'prev_lesson_obj': prev_lesson_obj,
        'user_session': initial_user_session,
        'lq_rv': lq_rv,
        'pcqid': course_lesson_obj.id
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
    # question_test_cases_rv = []
    # for qtc_obj in question_test_cases:
    #     print('qtc-input-param:', qtc_obj.input_param)
    #     input_param_str = ','.join(list(ast.literal_eval(qtc_obj.input_param)))
    #     question_test_cases_rv.append([qtc_obj.id, input_param_str, qtc_obj.correct_output])

    user_code_obj = None
    code_id = None
    
    user_code_objects = PythonLessonUserCode.objects.filter(
        lesson_question_obj = pc_question_obj,
        user_auth_obj = user_auth_obj
    )
    if len(user_code_objects) > 0:
        user_code_obj = user_code_objects[0]
        code_id = user_code_obj.id


    next_order_number = pc_question_obj.order_number + 1
    prev_order_number = pc_question_obj.order_number - 1
    next_question_obj = None
    if PythonLessonQuestion.objects.filter(order_number = next_order_number, course_lesson_obj = pc_question_obj.course_lesson_obj).count() > 0:
        next_question_obj = PythonLessonQuestion.objects.get(order_number = next_order_number, course_lesson_obj = pc_question_obj.course_lesson_obj)

    prev_question_obj = None
    if PythonLessonQuestion.objects.filter(order_number = prev_order_number, course_lesson_obj = pc_question_obj.course_lesson_obj).count() > 0:
        prev_question_obj = PythonLessonQuestion.objects.get(order_number = prev_order_number, course_lesson_obj = pc_question_obj.course_lesson_obj)

    user_q_submissions = PythonLessonQuestionUserSubmission.objects.filter(user_auth_obj = user_auth_obj, lesson_question_obj = pc_question_obj)
    q_complete_success = False
    for sub_obj in user_q_submissions:
        if sub_obj.complete:
            q_complete_success = True
            break

    user_conversation_objects = PythonLessonConversation.objects.filter(
        code_obj = user_code_obj,
        user_auth_obj = user_auth_obj
    ).order_by('created_at')

    print('user_conv_objects:', user_conversation_objects)
    print('code-id', code_id)

    return render(request, 'course_playground_environment_new.html', {
        'user_session': initial_user_session,
        'pcqid': pcqid,
        'pc_question_obj': pc_question_obj,
        'total_lesson_questions': PythonLessonQuestion.objects.filter(course_lesson_obj = pc_question_obj.course_lesson_obj).count(),

        'pt_course_test_case_examples': question_test_cases,
        'pt_course_test_case_examples_length': len(question_test_cases),

        # 'pt_course_test_case_examples': question_test_cases_rv,
        # 'pt_course_test_case_examples_length': len(question_test_cases_rv),

        'code_id': code_id,
        'user_code_obj': user_code_obj,

        'next_question_obj': next_question_obj,
        'prev_question_obj': prev_question_obj,

        'total_user_submissions': len(user_q_submissions),
        'q_complete_success': q_complete_success,

        'user_conversation_objects': user_conversation_objects
    })



def new_course_random_question(request):
    
    initial_user_session = request.session.get("user")
    user_auth_obj = None    
    if initial_user_session is not None:
        user_oauth_objects = UserOAuth.objects.filter(email = initial_user_session['userinfo']['email'])
        if len(user_oauth_objects) > 0:
            user_auth_obj = user_oauth_objects[0]

    # lesson_one_obj = PythonCourseLesson.objects.filter(lesson_title__contains='Lesson 1')[0]
    # lesson_two_obj = PythonCourseLesson.objects.filter(lesson_title__contains='Lesson 2')[0]

    # all_lesson_questions = PythonLessonQuestion.objects.filter(
    #     course_lesson_obj__in = (lesson_one_obj.id, lesson_two_obj.id)
    # )
    
    all_lesson_questions = PythonLessonQuestion.objects.exclude(order_number = 1)
    rv_all_lesson_questions = []
    if user_auth_obj is not None:
        user_question_submissions = PythonLessonQuestionUserSubmission.objects.filter(
            user_auth_obj = user_auth_obj
        )
        user_sub_question_objects = [user_sub_q.lesson_question_obj.id for user_sub_q in user_question_submissions]
        for aqobj in all_lesson_questions:
            if aqobj.id not in user_sub_question_objects:
                rv_all_lesson_questions.append(aqobj)
    else:
        rv_all_lesson_questions = all_lesson_questions

    if len(rv_all_lesson_questions) == 0:  # user finished all questions!
        return redirect('new_course_home')
    else:
        import random
        rnd_q_obj = random.choice(rv_all_lesson_questions)
        response = redirect('new_course_playground')
        response['Location'] += '?pcqid=' + str(rnd_q_obj.id)
        return response


def new_course_handle_user_message(request):

    initial_user_session = request.session.get("user")

    if request.method == 'POST':

        user_question = request.POST['message'].strip()
        user_code = request.POST['user_code'].strip()     
        user_code = user_code.replace('`', '"').strip()

        user_cid = request.POST['cid']
        user_pclid = request.POST['pclid']

        lesson_ques_obj = None
        if user_pclid != 'None':
            lesson_question_objects = PythonLessonQuestion.objects.filter(id = user_pclid)
            if len(lesson_question_objects) > 0:
                lesson_ques_obj = lesson_question_objects[0]

        initial_user_session = request.session.get('user')
        if initial_user_session is None:
            previous_message_st = request.POST['previous_messages'].strip()

            programming_problem = lesson_ques_obj.question_text
            model_response_dict = main_utils.main_handle_question(
                question = user_question,
                programming_problem = programming_problem,
                student_code = user_code,
                previous_chat_history_st = previous_message_st
            )
            return JsonResponse({'success': True, 'response': model_response_dict})


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
            programming_problem = lesson_ques_obj.question_text,
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



def new_course_video_handle_message(request):
    
    initial_user_session = request.session.get("user")

    if request.method == 'POST':

        user_question = request.POST['message'].strip()

        initial_user_session = request.session.get('user')
        if initial_user_session is None:
            
            previous_message_st = request.POST['previous_messages'].strip()

            model_response_dict = main_utils.general_tutor_handle_question(
                question = user_question,
                previous_chat_history_st = previous_message_st
            )
            
            return JsonResponse({'success': True, 'response': model_response_dict})

        else:
            
            lesson_pclid = request.POST['pclid']
            # TODO: add filter here just in case no lesson associated with id
            pcl_obj = PythonCourseLesson.objects.get(id = lesson_pclid)

            user_oauth_obj = UserOAuth.objects.get(email = initial_user_session['userinfo']['email'])
            prev_conversation_history = []

            prev_conversation_messages = PythonLessonVideoConversation.objects.filter(
                user_auth_obj = user_oauth_obj,
                course_lesson_obj = pcl_obj
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
            
            model_response_dict = main_utils.general_tutor_handle_question(
                question = user_question,
                previous_chat_history_st = prev_conversation_st
            )

            py_conv_obj = PythonLessonVideoConversation.objects.create(
                user_auth_obj = user_oauth_obj,
                course_lesson_obj = pcl_obj,
                question = user_question,
                response = model_response_dict['response']
            )
            py_conv_obj.save()

            return JsonResponse({'success': True, 'response': model_response_dict})
            




### Python-Course-Admin ###


# def new_course_admin(request):
def admin_new_course_dashboard(request):
    user_is_admin = request.user.is_superuser
    if not user_is_admin:  # exempt from auth check; has visibility into all user's code
        return redirect('landing')
    
    return render(request, 'course_lesson_admin.html')


def admin_new_course_lesson_management(request):
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

            if PythonCourseLesson.objects.all().count() != 0:
                next_order_number = PythonCourseLesson.objects.latest('id').order_number + 1
            else:
                next_order_number = 0
            
            pc_lesson_obj = PythonCourseLesson.objects.create(
                lesson_title = lesson_name,
                lesson_description = lesson_description,
                lesson_video = lesson_yt_url,
                order_number = next_order_number
            )
            pc_lesson_obj.save()

        return redirect('admin_new_course_lesson_management')


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
def admin_new_course_lesson_order_management(request):
    
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


def admin_new_course_lesson_delete(request):

    if request.method == 'POST':
        if not request.user.is_superuser:
            return JsonResponse({'success': False})

        PythonCourseLesson.objects.filter(id = request.POST['lid']).delete()
        return JsonResponse({'success': True})



def admin_new_course_lesson_question_management(request, lid):
    pc_obj = get_object_or_404(PythonCourseLesson, id = lid)

    if request.method == 'POST':
        print('POST DATA:', request.POST)

        if 'question-id-value' in request.POST:
            qid = request.POST['question-id-value']
            pyq_obj = PythonLessonQuestion.objects.get(id = qid)

            pyq_obj.question_name = request.POST['question-name'].strip()
            pyq_obj.question_text = request.POST['question-text'].strip()
            pyq_obj.save()

            tc_input_zero, tc_output_zero = None, None
            if 'test-input-0' in request.POST:
                tc_input_zero, tc_output_zero = request.POST['test-input-0'].strip(), request.POST['test-output-0'].strip()

            tc_input_one, tc_output_one = None, None
            if 'test-input-1' in request.POST:
                tc_input_one, tc_output_one = request.POST['test-input-1'].strip(), request.POST['test-output-1'].strip()

            tc_input_two, tc_output_two = None, None
            if 'test-input-2' in request.POST:
                tc_input_two, tc_output_two = request.POST['test-input-2'].strip(), request.POST['test-output-2'].strip()

            tc_input_three, tc_output_three = None, None
            if 'test-input-3' in request.POST:
                tc_input_three, tc_output_three = request.POST['test-input-3'].strip(), request.POST['test-output-3'].strip()
            
            tc_input_four, tc_output_four = None, None
            if 'test-input-4' in request.POST:
                tc_input_four, tc_output_four = request.POST['test-input-4'].strip(), request.POST['test-output-4'].strip()
            
            tc_input_five, tc_output_five = None, None
            if 'test-input-5' in request.POST:
                tc_input_five, tc_output_five = request.POST['test-input-5'].strip(), request.POST['test-output-5'].strip()
            
            tc_input_six, tc_output_six = None, None
            if 'test-input-6' in request.POST:
                tc_input_six, tc_output_six = request.POST['test-input-6'].strip(), request.POST['test-output-6'].strip()

            PythonLessonQuestionTestCase.objects.filter(
                lesson_question_obj = pyq_obj
            ).delete()

            
            if tc_input_zero is not None:
                tq_tc_obj = PythonLessonQuestionTestCase.objects.create(
                    lesson_question_obj = pyq_obj,
                    input_param = tc_input_zero,
                    correct_output = tc_output_zero
                )
                tq_tc_obj.save()

            if tc_input_one is not None:
                tq_tc_obj = PythonLessonQuestionTestCase.objects.create(
                    lesson_question_obj = pyq_obj,
                    input_param = tc_input_one,
                    correct_output = tc_output_one
                )
                tq_tc_obj.save()
            
            if tc_input_two is not None:
                tq_tc_obj = PythonLessonQuestionTestCase.objects.create(
                    lesson_question_obj = pyq_obj,
                    input_param = tc_input_two,
                    correct_output = tc_output_two
                )
                tq_tc_obj.save()

            if tc_input_three is not None:
                tq_tc_obj = PythonLessonQuestionTestCase.objects.create(
                    lesson_question_obj = pyq_obj,
                    input_param = tc_input_three,
                    correct_output = tc_output_three
                )
                tq_tc_obj.save()
            
            if tc_input_four is not None:
                tq_tc_obj = PythonLessonQuestionTestCase.objects.create(
                    lesson_question_obj = pyq_obj,
                    input_param = tc_input_four,
                    correct_output = tc_output_four
                )
                tq_tc_obj.save()
            
            if tc_input_five is not None:
                tq_tc_obj = PythonLessonQuestionTestCase.objects.create(
                    lesson_question_obj = pyq_obj,
                    input_param = tc_input_five,
                    correct_output = tc_output_five
                )
                tq_tc_obj.save()

            if tc_input_six is not None:
                tq_tc_obj = PythonLessonQuestionTestCase.objects.create(
                    lesson_question_obj = pyq_obj,
                    input_param = tc_input_six,
                    correct_output = tc_output_six
                )
                tq_tc_obj.save()


        else:
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
            
            if PythonLessonQuestion.objects.all().count() > 0:
                next_order_number = PythonLessonQuestion.objects.latest('id').order_number + 1
            else:
                next_order_number = 0

            tc_question_obj = PythonLessonQuestion.objects.create(
                question_name = question_name, 
                question_text = question_text,
                course_lesson_obj = course_lesson_obj,
                order_number = next_order_number
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


        return redirect('admin_new_course_lesson_question_management', lid = pc_obj.id)


    pyq_objects = PythonLessonQuestion.objects.filter(
        course_lesson_obj = pc_obj
    ).order_by('order_number')

    # TODO: 
        # adding test-cases for the question
    if 'question-edit-id' in request.GET:
        if not request.user.is_superuser:
            return JsonResponse({'success': False})

        question_edit_id = request.GET.get('question-edit-id')

        current_question_obj = PythonLessonQuestion.objects.get(id = question_edit_id)
        associated_question_test_case_objects = PythonLessonQuestionTestCase.objects.filter(lesson_question_obj = current_question_obj)

        q_test_cases_rv = []
        for idx in range(0, len(associated_question_test_case_objects)):
            q_test_cases_rv.append([idx, associated_question_test_case_objects[idx]])

        return render(request, 'course_question_management.html', {
            'all_question_objects': pyq_objects,
            'current_question_obj': current_question_obj,
            'associated_question_test_case_objects': q_test_cases_rv,
            'question_edit': True
        })

    return render(request, 'course_question_management.html', {
        'lesson_obj': pc_obj,
        'all_question_objects': pyq_objects,
        'current_lesson_obj': pc_obj
    })
    


def admin_new_course_question_delete(request):

    if request.method == 'POST':
        if not request.user.is_superuser:
            return JsonResponse({'success': False})

        # PythonCourseLesson.objects.filter(id = request.POST['lid']).delete()
        PythonLessonQuestion.objects.filter(id = request.POST['qid']).delete()
        return JsonResponse({'success': True})


@csrf_exempt
def admin_new_course_question_order_management(request):
     if request.method == 'POST':

        if not request.user.is_superuser:
            return JsonResponse({'success': False})

        d = json.loads(request.POST.get('data', ''))
        all_items = d['all_items']
        for obj_id in all_items:
            order_num = all_items[obj_id]
            cobj = PythonLessonQuestion.objects.get(id = obj_id)
            cobj.order_number = order_num
            cobj.save()

        return JsonResponse({'success': True})



def admin_new_course_question_view(request, qid):
    question_obj = get_object_or_404(PythonLessonQuestion, id = qid)
    return render(request, 'course_question_view.html', {
        'question_object': question_obj
    })



import ast

def new_course_handle_solution_submit(request):

    if request.method == 'POST':

        print('POST-DATA:', request.POST)

        user_code = request.POST['user_code'].strip()
        user_code = user_code.replace('`', '"').strip()
        user_cid = request.POST['cid']
        user_pclid = request.POST['pclid']
        
        lesson_ques_obj = None
        if user_pclid != 'None':
            lesson_question_objects = PythonLessonQuestion.objects.filter(id = user_pclid)
            if len(lesson_question_objects) > 0:
                lesson_ques_obj = lesson_question_objects[0]


        pt_q_test_cases = PythonLessonQuestionTestCase.objects.filter(lesson_question_obj = lesson_ques_obj)
        test_case_correct_list = []
        q_complete_success = True
        function_time_out_error = False
        for qtc_obj in pt_q_test_cases:
            tc_input = qtc_obj.input_param
            tc_output = qtc_obj.correct_output

            # tc_input_list = ast.literal_eval(tc_input)
            print('tc-input:', tc_input)
            tc_input_list = eval(tc_input)
            tc_output = eval(tc_output)

            print('tc_input_list', tc_input_list)

            try:
                valid_solution_dict = new_question_solution_check(
                    source_code = user_code,
                    input_param = tc_input_list,
                    output_param = tc_output,
                )
            except:
                valid_solution_dict = {'success': False, 'message': 'Function timed out.', 'user_function_output': None}
                function_time_out_error = True
                # q_complete_success = False
                break

            print('valid-solution-dict:', valid_solution_dict)

            valid_solution = valid_solution_dict['success']

            tc_status = 0
            if valid_solution:
                tc_status = 1

            else:  # user got an answer wrong; unsuccessfully completed
                q_complete_success = False

            test_case_correct_list.append({
                'user_output_id_text': f'user_output_{ qtc_obj.id }',
                'tc_id_text': f'status_{ qtc_obj.id }',
                'status': tc_status,
                'message': valid_solution_dict['message'],
                'user_function_output': valid_solution_dict['user_function_output']
            })


        initial_user_session = request.session.get('user')
        if initial_user_session is None:

            return JsonResponse({
                'success': True, 
                'test_case_list': test_case_correct_list,
                'function_time_out_error': function_time_out_error
            })

        else:
            user_oauth_obj = UserOAuth.objects.get(email = initial_user_session['userinfo']['email'])

            if user_cid == 'None':
                rnd_code_filename = lesson_ques_obj.question_name
                uc_obj = PythonLessonUserCode.objects.create(
                    user_auth_obj = user_oauth_obj,
                    code_unique_name = rnd_code_filename,
                    user_code = user_code,
                    lesson_question_obj = lesson_ques_obj
                )
                uc_obj.save()

                pq_subm_obj = PythonLessonQuestionUserSubmission.objects.create(
                    user_auth_obj = user_oauth_obj,
                    lesson_question_obj = lesson_ques_obj,
                    code_str = user_code,
                    complete = q_complete_success
                )
                pq_subm_obj.save()

                total_submissions = PythonLessonQuestionUserSubmission.objects.filter(
                    user_auth_obj = user_oauth_obj
                ).count()

                return JsonResponse({
                    'success': True, 
                    'cid': uc_obj.id, 
                    'test_case_list': test_case_correct_list,
                    'q_complete_success': q_complete_success,
                    'total_q_submissions': total_submissions,
                    'function_time_out_error': function_time_out_error
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

                pq_subm_obj = PythonLessonQuestionUserSubmission.objects.create(
                    user_auth_obj = user_oauth_obj,
                    lesson_question_obj = lesson_ques_obj,
                    code_str = user_code,
                    complete = q_complete_success
                )
                pq_subm_obj.save()

                total_submissions = PythonLessonQuestionUserSubmission.objects.filter(
                    user_auth_obj = user_oauth_obj
                ).count()

                return JsonResponse({
                    'success': True, 
                    'cid': uc_obj.id, 
                    'test_case_list': test_case_correct_list,
                    'q_complete_success': q_complete_success,
                    'total_q_submissions': total_submissions,
                    'function_time_out_error': function_time_out_error
                })


        # initial_user_session = request.session.get('user')
        # if initial_user_session is None:

        #     user_prev_messages = request.POST['previous_messages']
        
        #     model_response_dict = main_utils.main_handle_question(
        #         question = user_message,
        #         student_code = user_code,
        #         previous_chat_history_st = user_prev_messages
        #     )

        #     return JsonResponse({'success': True, 'response': model_response_dict, 'test_case_list': test_case_correct_list})

        # else:

        #     user_oauth_obj = UserOAuth.objects.get(email = initial_user_session['userinfo']['email'])
        
        #     prev_conversation_history = []
        #     if user_cid != 'None':

        #         prev_conversation_messages = PythonLessonConversation.objects.filter(
        #             user_auth_obj = user_oauth_obj,
        #             code_obj_id = user_cid
        #         ).order_by('-created_at')

        #         if len(prev_conversation_messages) > 0:
        #             for uc_obj in prev_conversation_messages[:5]:
        #                 uc_question = uc_obj.question
        #                 uc_response = uc_obj.response
        #                 prev_conversation_history.append(f"Question: { uc_question }")
        #                 prev_conversation_history.append(f"Response: { uc_response }")


        #     prev_conversation_st = ''
        #     if len(prev_conversation_history) > 0:
        #         prev_conversation_st = '\n'.join(prev_conversation_history)
            
        #     model_response_dict = main_utils.main_handle_question(
        #         question = user_message,
        #         student_code = user_code,
        #         previous_chat_history_st = prev_conversation_st
        #     )

        #     if user_cid == 'None':

        #         rnd_code_filename = lesson_ques_obj.question_name

        #         uc_obj = PythonLessonUserCode.objects.create(
        #             user_auth_obj = user_oauth_obj,
        #             code_unique_name = rnd_code_filename,
        #             user_code = user_code,
        #             lesson_question_obj = lesson_ques_obj
        #         )
        #         uc_obj.save()

        #         return JsonResponse({
        #             'success': True, 
        #             'cid': uc_obj.id, 
        #             'response': model_response_dict, 
        #             'test_case_list': test_case_correct_list
        #         })

        #     else:
        #         uc_objects = PythonLessonUserCode.objects.filter(
        #             id = user_cid, 
        #             user_auth_obj = user_oauth_obj
        #         )
        #         if len(uc_objects) == 0:
        #             return JsonResponse({'success': False, 'response': 'Object id not found.'})

        #         uc_obj = uc_objects[0]
        #         uc_obj.lesson_question_obj = lesson_ques_obj
        #         uc_obj.user_code = user_code
        #         uc_obj.save()

        #         return JsonResponse({
        #             'success': True, 
        #             'cid': uc_obj.id, 
        #             'response': model_response_dict, 
        #             'test_case_list': test_case_correct_list
        #         })




def new_course_handle_ai_feedback(request):
    
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

        initial_user_session = request.session.get('user')
        if initial_user_session is None:

            user_prev_messages = request.POST['previous_messages']
        
            model_response_dict = main_utils.main_handle_question(
                question = user_message,
                programming_problem = lesson_ques_obj.question_text,
                student_code = user_code,
                previous_chat_history_st = user_prev_messages
            )

            return JsonResponse({'success': True, 'response': model_response_dict})

        else:
            
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
            
            model_response_dict = main_utils.main_handle_question(
                question = user_message,
                programming_problem = lesson_ques_obj.question_text,
                student_code = user_code,
                previous_chat_history_st = prev_conversation_st
            )

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

                return JsonResponse({
                    'success': True, 
                    'cid': uc_obj.id, 
                    'response': model_response_dict, 
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

                ur_obj = PythonLessonConversation.objects.create(
                    user_auth_obj = user_oauth_obj,
                    code_obj = uc_obj,
                    question = model_response_dict['question'],
                    question_prompt = model_response_dict['q_prompt'],
                    response = model_response_dict['response'],
                )
                ur_obj.save()

                return JsonResponse({
                    'success': True, 
                    'cid': uc_obj.id, 
                    'response': model_response_dict, 
                })

