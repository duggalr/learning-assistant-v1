from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_GET, require_POST
import logging

from .models import *
from .scripts import utils, open_ai_utils


### Decorators ###

def user_authenticated_required(view_func):
    """
    Custom decorator to check if the user is authenticated.
    """
    def wrapper(request, *args, **kwargs):
        custom_user_id = request.session.get('custom_user_uuid', None)
        if custom_user_id is not None:
            custom_user_obj = CustomUser.objects.get(id = custom_user_id)
            if custom_user_obj.oauth_user is not None:
                return view_func(request, *args, **kwargs)
            else:
                return redirect('landing')
        else:
            return redirect('landing')
    return wrapper



### Generic Views ###

def landing(request):
    custom_user_obj = utils._get_customer_user(request)
    anon_user = utils._check_if_anon_user(custom_user_obj)

    return render(request, 'generic/landing.html',  {
        'anon_user': anon_user,
        'custom_user_obj_id': custom_user_obj.id
    })

def about(request):
    custom_user_obj = utils._get_customer_user(request)
    anon_user = utils._check_if_anon_user(custom_user_obj)

    return render(request, 'generic/about.html', {
        'anon_user': anon_user,
        'custom_user_obj_id': custom_user_obj.id
    })

def blog(request):
    custom_user_obj = utils._get_customer_user(request)
    anon_user = utils._check_if_anon_user(custom_user_obj)

    return render(request, 'generic/blog.html', {
        'anon_user': anon_user,
        'custom_user_obj_id': custom_user_obj.id
    })

def blog_v1_release(request):
    custom_user_obj = utils._get_customer_user(request)
    anon_user = utils._check_if_anon_user(custom_user_obj)

    return render(request, 'generic/blog_v1_release.html', {
        'anon_user': anon_user,
        'custom_user_obj_id': custom_user_obj.id
    })

def faq(request):
    custom_user_obj = utils._get_customer_user(request)
    anon_user = utils._check_if_anon_user(custom_user_obj)

    return render(request, 'generic/faq.html', {
        'anon_user': anon_user,
        'custom_user_obj_id': custom_user_obj.id
    })




### Playground General CS Tutor Views ###

def playground(request):
    custom_user_obj = utils._get_customer_user(request)
    anon_user = utils._check_if_anon_user(custom_user_obj)

    code_id = request.GET.get('cid', None)
    user_language_choice = request.GET.get('lg', None)

    uc_obj = None
    user_conversation_objects = []
    if code_id is not None and not anon_user:
        uc_obj = get_object_or_404(PlaygroundCode, id = code_id)
        user_conversation_objects = PlaygroundConversation.objects.filter(
            code_obj = uc_obj
        ).order_by('created_at')

    current_user_email = None
    if custom_user_obj.oauth_user is not None:
        current_user_email = custom_user_obj.oauth_user.email

    rv = {
        'anon_user': anon_user,
        'custom_user_obj': custom_user_obj,
        'custom_user_obj_id': custom_user_obj.id,
        'current_user_email': current_user_email,
        'uc_obj': uc_obj,
        'user_conversation_objects': user_conversation_objects,
        'user_language_choice': user_language_choice,
        'code_id': None
    }
    if code_id is not None and not anon_user:
        rv['code_id'] = code_id

    return render(request, 'assistant/playground.html', rv)


def general_cs_tutor(request):

    custom_user_obj = utils._get_customer_user(request)
    anon_user = utils._check_if_anon_user(custom_user_obj)

    tchid = request.GET.get('tchid', None)
    
    parent_conv_objects = UserGeneralTutorParent.objects.filter(
        user_obj = custom_user_obj
    )

    user_full_conversation_list = []
    cv_count = 1
    for pc_obj in parent_conv_objects:
        past_conv_messages = UserGeneralTutorConversation.objects.filter(
            parent_obj = pc_obj
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
    if tchid is not None and not anon_user:
        parent_conv_objects = UserGeneralTutorParent.objects.filter(
            id = tchid
        )
        if len(parent_conv_objects) == 0:
            current_cid_parent_conv_obj = None
        else:
            current_cid_parent_conv_obj = parent_conv_objects[0]
            current_cid_past_messages = UserGeneralTutorConversation.objects.filter(
                parent_obj = current_cid_parent_conv_obj
            )

    current_user_email = None
    if custom_user_obj.oauth_user is not None:
        current_user_email = custom_user_obj.oauth_user.email

    return render(request, 'assistant/general_cs_tutor_chat.html', {
        'anon_user': anon_user,
        'custom_user_obj': custom_user_obj,
        'custom_user_obj_id': custom_user_obj.id,
        'current_user_email': current_user_email,
        'all_user_conversation_list': user_full_conversation_list,
        'current_conversation_parent_object': current_cid_parent_conv_obj,
        'current_conversation_list': current_cid_past_messages,
    })


@user_authenticated_required
def user_dashboard(request):
    
    custom_user_obj = utils._get_customer_user(request)
    anon_user = utils._check_if_anon_user(custom_user_obj)

    user_code_objects = PlaygroundCode.objects.filter(
        user_obj = custom_user_obj
    ).order_by('-updated_at')

    final_rv = []
    for uc_obj in user_code_objects:
        us_conv_objects_count = PlaygroundConversation.objects.filter(code_obj = uc_obj).count()
        final_rv.append({'code_obj': uc_obj, 'user_conv_obj_count': us_conv_objects_count})

    current_user_email = None
    if custom_user_obj.oauth_user is not None:
        current_user_email = custom_user_obj.oauth_user.email

    return render(request, 'assistant/dashboard.html', {
        'anon_user': anon_user,
        'custom_user_obj': custom_user_obj,
        'custom_user_obj_id': custom_user_obj.id,
        'current_user_email': current_user_email,
        'user_code_list': final_rv
    })



### Ajax Functions ###

@require_POST
def save_user_playground_code(request):
    
    custom_user_obj_id = request.session.get('custom_user_uuid', None)
    user_err, user_err_message = utils._is_bad_user_session(session_data = request.session)
    if user_err:
        return JsonResponse({'success': False, 'response': user_err_message})
    else:
        custom_user_obj = CustomUser.objects.get(id = custom_user_obj_id)

    cid = request.POST['cid']
    user_code = request.POST['user_code'].strip()
    user_code = user_code.replace('`', '"').strip()    

    if cid == '':
        rnd_code_filename = utils._generate_random_string(k = 10)

        uc_obj = PlaygroundCode.objects.create(
            user_obj = custom_user_obj,
            code_unique_name = rnd_code_filename,
            user_code = user_code
        )
        uc_obj.save()
        return JsonResponse({'success': True, 'cid': uc_obj.id, 'code_file_name': uc_obj.code_unique_name})

    else:
        uc_objects = PlaygroundCode.objects.filter(
            id = cid,
            user_obj = custom_user_obj
        )
        if len(uc_objects) == 0:
            return JsonResponse({'success': False, 'response': 'Object not found.'})
        
        uc_obj = uc_objects[0]
        uc_obj.user_code = user_code
        uc_obj.save()
        return JsonResponse({'success': True, 'cid': uc_obj.id})


@require_POST
def handle_playground_user_message(request):
    
    custom_user_obj_id = request.session.get('custom_user_uuid', None)
    user_err, user_err_message = utils._is_bad_user_session(session_data = request.session)
    if user_err:
        return JsonResponse({'success': user_err, 'response': user_err_message})
    else:
        custom_user_obj = CustomUser.objects.get(id = custom_user_obj_id)

    user_question = request.POST['message'].strip()
    user_code_obj_id = request.POST['cid']
    user_code = request.POST['user_code'].strip()
    user_code = user_code.replace('`', '"').strip()

    prev_conversation_history_str = ''
    if user_code_obj_id == '':
        uc_obj = utils._create_playground_code_object(
            custom_user_obj=custom_user_obj,
            user_code=user_code,
        )
    else:
        user_code_objects = PlaygroundCode.objects.filter(id = user_code_obj_id)
        if len(user_code_objects) == 0:
            return JsonResponse({'success': False, 'response': 'Could not find associated code object.'})
        else:
            uc_obj = user_code_objects[0]

        pg_conversation_objects = PlaygroundConversation.objects.filter(
            code_obj = uc_obj
        )

        prev_cv_list = []
        for pg_conv_obj in pg_conversation_objects[:open_ai_utils.MAX_CONVERSATION_HISTORY_LENGTH]:
            uc_question = pg_conv_obj.question
            uc_response = pg_conv_obj.response
            prev_cv_list.append(f"Question: { uc_question }")
            prev_cv_list.append(f"Response: { uc_response }")

        if len(prev_cv_list) > 0:
            prev_conversation_history_str = '\n'.join(prev_cv_list)

    op_ai_wrapper = open_ai_utils.OpenAIWrapper()
    model_response_dict = op_ai_wrapper.handle_playground_code_question(
        question = user_question,
        student_code = user_code, 
        previous_chat_history = prev_conversation_history_str
    )

    pg_new_cv_obj = PlaygroundConversation.objects.create(
        code_obj = uc_obj,
        question = model_response_dict['question'],
        question_prompt = model_response_dict['q_prompt'],
        response = model_response_dict['response']
    )
    pg_new_cv_obj.save()

    model_response_dict['cid'] = uc_obj.id
    model_response_dict['code_file_name'] = uc_obj.code_unique_name
    return JsonResponse({'success': True, 'response': model_response_dict})


@require_POST
def handle_playground_file_name_change(request):

    # custom_user_obj_id = request.session.get('custom_user_uuid', None)
    # print(f"custom-user-obj-id: {custom_user_obj_id} | type: {type(custom_user_obj_id)}")
    # user_err, user_err_message = utils._is_bad_user_session(session_data = request.session)
    # if user_err:
    #     return JsonResponse({'success': user_err, 'response': user_err_message})
    # else:
    #     custom_user_obj = CustomUser.objects.get(id = custom_user_obj_id)

    custom_user_obj_id = request.session.get('custom_user_uuid', None)
    user_err, user_err_message = utils._is_bad_user_session(session_data = request.session)
    if user_err:
        return JsonResponse({'success': user_err, 'response': user_err_message})
    else:
        custom_user_obj_id = str(custom_user_obj_id)
        custom_user_obj = CustomUser.objects.get(id = custom_user_obj_id)

    # custom_user_obj_id = request.POST['custom_user_obj_id']
    cid = request.POST['cid']
    new_file_name = request.POST['new_file_name'].strip()
    user_code = request.POST['user_code'].strip()
    user_code = user_code.replace('`', '"').strip()

    print("CID IS: ", cid)

    if cid == 'None':
        uc_obj = PlaygroundCode.objects.create(
            user_obj = custom_user_obj,
            code_unique_name = new_file_name,
            user_code = user_code
        )
        uc_obj.save()
    else:
        uc_obj = PlaygroundCode.objects.get(
            id = cid,
            user_obj = custom_user_obj
        )
        uc_obj.code_unique_name = new_file_name
        uc_obj.save()

    return JsonResponse({'success': True, 'cid': uc_obj.id, 'new_file_name': new_file_name})


@require_POST
def handle_general_tutor_user_message(request):

    custom_user_obj_id = request.session.get('custom_user_uuid', None)
    user_err, user_err_message = utils._is_bad_user_session(session_data = request.session)
    if user_err:
        return JsonResponse({'success': user_err, 'response': user_err_message})
    else:
        custom_user_obj = CustomUser.objects.get(id = custom_user_obj_id)

    general_tutor_parent_obj_id = request.POST['general_tutor_parent_obj_id']
    user_message = request.POST['message'].strip()
    
    prev_conversation_st = ''
    parent_chat_obj = None
    if general_tutor_parent_obj_id == '':
        parent_chat_obj = utils._create_general_tutor_parent_object(
            custom_user_obj=custom_user_obj,
        )
    else:
        parent_chat_objects = UserGeneralTutorParent.objects.filter(
            id = general_tutor_parent_obj_id
        )
        if len(parent_chat_objects) == 0:
            return JsonResponse({'success': False, 'response': 'Object not found.'})

        parent_chat_obj = parent_chat_objects[0]

        past_conversation_objects = UserGeneralTutorConversation.objects.filter(
            parent_obj = parent_chat_obj
        ).order_by('-created_at')

        prev_conversation_history = []
        for uc_tut_obj in past_conversation_objects[:open_ai_utils.MAX_CONVERSATION_HISTORY_LENGTH]:
            uc_question = uc_tut_obj.question
            uc_response = uc_tut_obj.response
            prev_conversation_history.append(f"Question: { uc_question }")
            prev_conversation_history.append(f"Response: { uc_response }")

        prev_conversation_st = '\n'.join(prev_conversation_history).strip()
    
    op_ai_wrapper = open_ai_utils.OpenAIWrapper()
    model_response_dict = op_ai_wrapper.handle_general_tutor_message(
        question = user_message,
        previous_chat_history_str = prev_conversation_st
    )

    uct_obj = UserGeneralTutorConversation.objects.create(
        parent_obj = parent_chat_obj,
        question = model_response_dict['student_response'],
        question_prompt = model_response_dict['q_prompt'],
        response = model_response_dict['response']
    )
    uct_obj.save()

    model_response_dict['uct_parent_obj_id'] = parent_chat_obj.id
    return JsonResponse({'success': True, 'response': model_response_dict})
