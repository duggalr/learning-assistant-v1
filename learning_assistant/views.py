from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse

from .models import *

# from acc.models import CustomUser, AnonUser
from .scripts import utils, open_ai_utils


def landing(request):
    custom_user_obj = utils._get_customer_user(request)
    anon_user = utils._check_if_anon_user(custom_user_obj)

    return render(request, 'generic/landing.html',  {
        'anon_user': anon_user
    })


def about(request):
    custom_user_obj = utils._get_customer_user(request)
    anon_user = utils._check_if_anon_user(custom_user_obj)

    return render(request, 'generic/about.html', {
        'anon_user': anon_user
    })


def playground(request):
    custom_user_obj = utils._get_customer_user(request)
    anon_user = utils._check_if_anon_user(custom_user_obj)

    code_id = request.GET.get('cid', None)

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

    return render(request, 'assistant/playground.html', {    
        'anon_user': anon_user,
        'custom_user_obj': custom_user_obj,
        'custom_user_obj_id': custom_user_obj.id,
        'current_user_email': current_user_email,
        'code_id': code_id,
        'uc_obj': uc_obj,
        'user_conversation_objects': user_conversation_objects,
    })


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
            id = tchid
        )
        if len(parent_conv_objects) == 0:
            current_cid_parent_conv_obj = None
        else:
            current_cid_parent_conv_obj = parent_conv_objects[0]
            current_cid_past_messages = UserGeneralTutorConversation.objects.filter(
                chat_parent_object = current_cid_parent_conv_obj
            )

    return render(request, 'assistant/general_cs_tutor_chat.html', {
        'anon_user': anon_user,
        'custom_user_obj': custom_user_obj,
        'custom_user_obj_id': custom_user_obj.id,
        'all_user_conversation_list': user_full_conversation_list,
        'current_conversation_parent_object': current_cid_parent_conv_obj,
        'current_conversation_list': current_cid_past_messages,
    })




def save_user_playground_code(request):

    custom_user_obj = utils._get_customer_user(request)

    if request.method == 'POST':

        print('save-user-code-POST:', request.POST)

        cid = request.POST['cid']

        # TODO: this should be fetched from the session-obj, not directly from the user
        custom_user_obj_id = request.POST['custom_user_obj_id']
        user_code = request.POST['user_code'].strip()
        user_code = user_code.replace('`', '"').strip()
        
        custom_user_objects = CustomUser.objects.filter(id = custom_user_obj_id)
        if len(custom_user_objects) == 0:
            return JsonResponse({'success': False, 'response': 'User not found.'})

        custom_user_obj = custom_user_objects[0]

        if cid == 'None':

            rnd_code_filename = utils._generate_random_string(k = 10)
            uc_obj = PlaygroundCode.objects.create(
                user_obj = custom_user_obj,
                code_unique_name = rnd_code_filename,
                user_code = user_code
            )
            uc_obj.save()

            return JsonResponse({'success': True, 'cid': uc_obj.id, 'code_file_name': uc_obj.code_unique_name})
    
        else:
            # uc_objects = UserCode.objects.filter(id = cid, user_auth_obj = user_auth_obj)

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


def handle_playground_user_message(request):

    if request.method == 'POST':
        # print('form-data:', request.POST)

        # existing_anon_user_id = request.POST['existing_anon_user_id']
        # user_question = request.POST['message'].strip()
        # user_code = request.POST['user_code'].strip()     
        # user_code = user_code.replace('`', '"').strip()
        # user_code_obj_id = request.POST['cid']

        custom_user_obj_id = request.POST['custom_user_obj_id']
        user_question = request.POST['message'].strip()
        user_code_obj_id = request.POST['cid']
        user_code = request.POST['user_code'].strip()
        user_code = user_code.replace('`', '"').strip()

        # TODO: passing user-obj-id directly proposes security-vuln <-- **FIX**
        custom_user_objects = CustomUser.objects.filter(id = custom_user_obj_id)
        if len(custom_user_objects) == 0:
            return JsonResponse({'success': False, 'response': 'User not found.'})

        custom_user_obj = custom_user_objects[0]

        # TODO: 
            # handling message for anon user in playground
                
        prev_conversation_history_str = ''
        if user_code_obj_id == 'None':
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

            # TODO: setting some sort of limit on past message history?
            prev_cv_list = []
            for pg_conv_obj in pg_conversation_objects:
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


def handle_playground_file_name_change(request):

    custom_user_obj = utils._get_customer_user(request)

    if request.method == 'POST':
        
        cid = request.POST['cid']
        custom_user_obj_id = request.POST['custom_user_obj_id']
        new_file_name = request.POST['new_file_name'].strip()
        user_code = request.POST['user_code'].strip()
        user_code = user_code.replace('`', '"').strip()

        custom_user_objects = CustomUser.objects.filter(id = custom_user_obj_id)        
        if len(custom_user_objects) == 0:
            return JsonResponse({'success': False, 'response': 'User not found.'})

        custom_user_obj = custom_user_objects[0]

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


def handle_general_tutor_user_message(request):
    # initial_user_session = request.session.get("user")

    if request.method == 'POST':
        print('cs-chat-data:', request.POST)

        custom_user_obj_id = request.POST['custom_user_obj_id']
        user_question = request.POST['message'].strip()
        user_code_obj_id = request.POST['cid']
        user_code = request.POST['user_code'].strip()
        user_code = user_code.replace('`', '"').strip()

        # 'general_cs_chat_parent_obj_id': general_cs_chat_parent_obj_id,
        #         'existing_anon_user_id': existing_anon_user_id,
        #         'message': messageText,
        #         'prev_conversation_history_st': prev_conversation_history_st,
        #         'uc_parent_obj_id': uc_parent_obj_id,
        #         'user_ct_obj_id': user_conversation_obj_id,
        #         csrfmiddlewaretoken: '{{ csrf_token }}'

        # TODO: passing user-obj-id directly proposes security-vuln <-- **FIX**
        custom_user_objects = CustomUser.objects.filter(id = custom_user_obj_id)
        if len(custom_user_objects) == 0:
            return JsonResponse({'success': False, 'response': 'User not found.'})

        custom_user_obj = custom_user_objects[0]





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



# TODO:
    # tutor user message and playground user message should be abstracted





### Course Gen ###

# def course_generation_background_chat(request):
#     # TODO: 
#         # for anon, fetch the user object and the conv-obj if any
#         # pass as hidden input id and go from there
    
#     custom_user_obj = utils._get_customer_user(request)
#     anon_user = utils._check_if_anon_user(custom_user_obj)

#     course_gen_bg_parent_objects = CourseGenBackgroundParent.objects.filter(
#         user_obj = custom_user_obj
#     )

#     # TODO: only using this for anno user
#     course_gen_obj = None
#     if len(course_gen_bg_parent_objects) > 0 and custom_user_obj.anon_user:
#         course_gen_obj = course_gen_bg_parent_objects[0]

#     user_conversation_objects = CourseGenBackgroundConversation.objects.filter(
#         bg_parent_obj = course_gen_obj
#     ).order_by('created_at')

#     return render(request, 'personal_course_gen/student_background_chat.html', {
#         'anon_user': anon_user,
#         'custom_user_obj': custom_user_obj,
#         'custom_user_obj_id': custom_user_obj.id,
#         'course_gen_bg_parent_obj': course_gen_obj,
#         'current_conversation_list': user_conversation_objects
#     })


# # TODO:
#     # need to handle both cases here
# def handle_course_generation_background_message(request):
        
#         if request.method == 'POST':

#             custom_user_obj_id = request.POST['custom_user_obj_id']
#             user_question = request.POST['message'].strip()
#             bg_chat_parent_obj_id = request.POST['bg_parent_obj_id']

#             custom_user_objects = CustomUser.objects.filter(id = custom_user_obj_id)
#             if len(custom_user_objects) == 0:
#                 return JsonResponse({'success': False, 'response': 'User not found.'})

#             custom_user_obj = custom_user_objects[0]

#             cg_bg_parent_obj = None
#             if bg_chat_parent_obj_id == 'None':
#                 cg_bg_parent_obj = CourseGenBackgroundParent.objects.create(
#                     custom_user_obj = custom_user_obj
#                 )
#             else:
#                 cg_bg_parent_objects = CourseGenBackgroundParent.objects.filter(
#                     user_obj = custom_user_obj,
#                     id = bg_chat_parent_obj_id
#                 )
#                 if len(cg_bg_parent_objects) > 0:
#                     cg_bg_parent_obj = cg_bg_parent_objects[0]
#                 else:
#                     return JsonResponse({'success': False, 'response': 'Object not found.'})

#             student_background_full_conversation_list = []
#             past_conv_objects = CourseGenBackgroundConversation.objects.filter(
#                 user_obj = custom_user_obj,
#                 bg_parent_obj = cg_bg_parent_obj
#             )
            
#             prev_conversation_history = []
#             for uc_tut_obj in past_conv_objects:
#                 uc_question = uc_tut_obj.question
#                 uc_response = uc_tut_obj.response
#                 prev_conversation_history.append(f"Question: { uc_question }")
#                 prev_conversation_history.append(f"Response: { uc_response }")

#             prev_conversation_st = '\n'.join(prev_conversation_history).strip()

#             print('PREVIOUS CONV:', prev_conversation_st)

#             op_ai_wrapper = open_ai_utils.OpenAIWrapper()
#             model_response_dict = op_ai_wrapper.handle_course_generation_message(
#                 student_response = user_question,
#                 previous_chat_history = prev_conversation_st,

#             )

#             course_bg_conv_obj = CourseGenBackgroundConversation.objects.create(
#                 bg_parent_obj = bg_chat_parent_obj_id,
#                 user_obj = custom_user_obj,
#                 question = user_question,
#                 question_prompt = model_response_dict['q_prompt'],
#                 response = model_response_dict['response']
#             )
#             course_bg_conv_obj.save()

