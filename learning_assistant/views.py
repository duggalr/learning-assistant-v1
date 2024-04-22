from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_GET, require_POST
import logging
import ast

from .models import *
from .scripts import utils, open_ai_utils, open_ai_course_gen_utils


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
        'anon_user': anon_user
    })


def about(request):
    custom_user_obj = utils._get_customer_user(request)
    anon_user = utils._check_if_anon_user(custom_user_obj)

    return render(request, 'generic/about.html', {
        'anon_user': anon_user
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


# TODO: will this be behind authentication?
@user_authenticated_required
def python_course_generation_main(request):

    pcid = request.GET.get('pcid', None)
    python_course_object = None
    # conversation_objects = []
    conversation_text_list = []
    student_background_object = None
    course_notes_objects = []
    exercise_objects = []
    # student_outline_dict = None
    student_outline_obj = None

    if pcid is not None:
        python_course_object = get_object_or_404(PythonCourseParent, id = pcid)
        
        conversation_objects = PythonCourseConversation.objects.filter(
            pg_obj = python_course_object
        ).order_by('created_at')
        
        for cobj in conversation_objects:
            # model_text_response = json.loads(cobj.response)['message_response'].strip()
            model_text_response_dict = ast.literal_eval(cobj.response)
            model_text_response = model_text_response_dict['message_response'].strip()
            conversation_text_list.append([cobj.question, model_text_response])
        
        # student_background_object = PythonCourseStudentBackground.objects.filter(
        #     pg_obj = python_course_object,
        # ).order_by('created_at')[0]

        student_outline_objects = PythonCourseStudentOutline.objects.filter(
            pg_obj = python_course_object
        )
        if len(student_outline_objects) > 0:
            student_outline_obj = student_outline_objects[0]
            # student_outline_dict = ast.literal_eval(student_outline_obj.json_response)
            student_outline_module_list = ast.literal_eval(student_outline_obj.module_list)
        
        # course_notes_objects = PythonCourseNote.objects.filter(
        #     pg_obj = python_course_object,
        # ).order_by('-created_at')
        
        # exercise_objects = PythonCourseExercise.objects.filter(
        #     pg_obj = python_course_object,
        # ).order_by('created_at')
    
    return render(
        request, 'python-course-gen/python_course_generation_main.html', {
            'course_obj': python_course_object,
            'course_obj_id': python_course_object.id if python_course_object is not None else None,
            # 'conversation_objects': conversation_objects,
            'conversation_objects': conversation_text_list,
            # 'student_background_object': student_background_object,
            'course_notes_objects': course_notes_objects,
            'exercise_objects': exercise_objects,
            'student_outline_object': student_outline_obj,
            'student_outline_module_list': student_outline_module_list,
            'recent_course_markdown': course_notes_objects[0].note if len(course_notes_objects) > 0 else None
        }
    )


@user_authenticated_required
def tmp_python_course_generated_list(request):
    custom_user_id = request.session['custom_user_uuid']
    custom_user_obj = CustomUser.objects.get(id = custom_user_id)
    course_objects = PythonCourseParent.objects.filter(
        user_obj = custom_user_obj
    ).order_by('created_at')
    return render(request, 'python-course-gen/tmp_course_list.html', {
        'course_objects': course_objects
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



import json

@require_POST
def handle_python_course_gen_user_message(request):

    custom_user_obj_id = request.session.get('custom_user_uuid', None)
    user_err, user_err_message = utils._is_bad_user_session(session_data = request.session)
    if user_err:
        return JsonResponse({'success': user_err, 'response': user_err_message})
    else:
        custom_user_obj = CustomUser.objects.get(id = custom_user_obj_id)

    print('request-post:', request.POST)

    pgen_obj_id = request.POST['parent_pgen_obj_id']
    user_code = request.POST['user_code'].strip()
    user_code = user_code.replace('`', '"').strip()
    user_message = request.POST['message'].strip()
    prev_conversation_history_str = ''

    if pgen_obj_id == '':
        pgen_obj = PythonCourseParent.objects.create(
            user_obj = custom_user_obj
        )
        pgen_obj.save()

    else:

        pgen_objects = PythonCourseParent.objects.filter(
            user_obj = custom_user_obj
        )
        if len(pgen_objects) == 0:
            return JsonResponse({'success': False, 'response': 'Could not find associated course object.'})

        pgen_obj = pgen_objects[0]

        pg_conversation_objects = PythonCourseConversation.objects.filter(
            pg_obj = pgen_obj
        )

        # TODO: appending the json to the prompt chat history <-- fix this and go from there; start with finalizing the generation/view of the course-outline
        prev_cv_list = []
        for pg_conv_obj in pg_conversation_objects[:open_ai_utils.MAX_CONVERSATION_HISTORY_LENGTH]:
            uc_question = pg_conv_obj.question
            uc_response = pg_conv_obj.response
            # uc_response_json = json.loads(uc_response)
            uc_response_json = ast.literal_eval(uc_response)
            uc_response_text_str = uc_response_json['message_response'].strip()
            prev_cv_list.append(f"Question: { uc_question }")
            # prev_cv_list.append(f"Response: { uc_response }")
            prev_cv_list.append(f"Response: { uc_response_text_str }")

        if len(prev_cv_list) > 0:
            prev_conversation_history_str = '\n'.join(prev_cv_list)

    # # user_past_information_dict = utils._fetch_past_user_context_information(
    # #     pcp_obj = pgen_obj
    # # )

    # student_background_full_str = ""
    # sb_objects = PythonCourseStudentBackground.objects.filter(
    #     pg_obj = pgen_obj
    # )
    # if len(sb_objects) > 0:
    #     student_background_full_str = sb_objects[0].student_background

    student_background_full_str = ""
    sbg_objects = PythonCourseStudentOutline.objects.filter(
        pg_obj = pgen_obj
    )
    if len(sbg_objects) > 0:
        student_background_full_str = sbg_objects[0].student_background

    # op_ai_wrapper = open_ai_utils.OpenAIWrapper()
    op_ai_wrapper = open_ai_course_gen_utils.OpenAIWrapper()
    model_response_dict = op_ai_wrapper.generate_router(
        previous_student_chat_history_str = prev_conversation_history_str,
        current_student_response_str = user_message,
        generated_learning_plan_str = student_background_full_str

        # current_student_response_str = user_message,
        # previous_student_chat_history_str = prev_conversation_history_str,
        # user_past_information_dict = user_past_information_dict
    )

    q_prompt = model_response_dict['q_prompt']
    model_response = model_response_dict['response']

    response_message_json_data = json.loads(model_response)
    function_type = response_message_json_data['function_type']
    message_response = response_message_json_data['message_response']
    
    ## Append past chat history
    tmp_past_st = f"Student Response: {user_message}\nYour Response: {message_response}\n"
    prev_conversation_history_str += tmp_past_st

    ## Save conversation chat history
    chat_cv_obj = PythonCourseConversation.objects.create(
        pg_obj = pgen_obj,
        question = user_message,
        question_prompt = q_prompt,
        response = str(response_message_json_data),
    )
    chat_cv_obj.save()

    ## Function Calls

    if function_type == 'generate_learning_plan':

        student_learning_outline_model_dict = op_ai_wrapper.generate_learning_outline(
            conversation_history = prev_conversation_history_str
        )
        student_learning_outline_model_json = json.loads(student_learning_outline_model_dict['response'])
        # generated_learning_plan_str_dict = str(student_learning_outline_model_json)

        pc_outline_obj = PythonCourseStudentOutline.objects.create(
            pg_obj = pgen_obj,
            student_background = student_learning_outline_model_json['student_background'],
            course_name = student_learning_outline_model_json['name'],
            course_description = student_learning_outline_model_json['description'],
            module_list = student_learning_outline_model_json['modules'],
        )
        pc_outline_obj.save()

        student_outline_modules_list = student_learning_outline_model_json['modules']
        for md in student_outline_modules_list:
            mc_obj = PythonCourseStudentModuleChild.objects.create(
                std_outline_obj = pc_outline_obj,
                module_number = md['module_number'],
                module_topic = md['module_topic'],
                module_description = md['module_description'],
            )
            mc_obj.save()

    elif function_type == 'generate_note_with_examples':

        note_topic = response_message_json_data['note_topic']
        # TODO: need to add limit to the previous conversation history
        
        tmp_note_dict = op_ai_wrapper.generate_new_note(
            topic_str = note_topic,
            conversation_history = prev_conversation_history_str
        )
        tmp_note_dict_json = json.loads(tmp_note_dict['response'])
        tmp_course_notes_text = tmp_note_dict_json['course_notes']
        
        pg_note_obj = PythonCourseNote.objects.create(
            pg_obj = pgen_obj,
            note = tmp_course_notes_text
        )
        pg_note_obj.save()
        
    elif function_type == 'generate_new_exercise_question':
        # # TODO: need to fetch the notes that will be used to generate the exercise, along with passing recent convesation history
        # op_ai_wrapper.generate_new_exercise(
        #     topic_str = ,
        #     conversation_history = ,
        # )

        raise NotImplementedError

    elif function_type == 'no_function_needed':
        # TODO: 
        pass

    
    # model_response_dict['pcid'] = pgen_obj.id
    # return JsonResponse({'success': True, 'response': model_response_dict})
    return JsonResponse({
        'success': True, 
        'function_type': function_type,
        'model_response_text': message_response,
        'pcid': pgen_obj.id
        # 'response': model_response_dict
    })

    # model_response_dict = op_ai_wrapper.handle_python_course_gen_message(
    #     current_student_response_str = user_message,
    #     previous_student_chat_history_str = prev_conversation_history_str,
    #     user_past_information_dict = user_past_information_dict
    # )

    # json_model_response = model_response_dict['response']
    # # model_text_reply = json_model_response['message_response']

    # if json_model_response['function_type'] == 'save_student_goals':
    #     student_goals = json_model_response['student_goals'].strip()
    #     pg_sb_obj = PythonCourseStudentBackground.objects.create(
    #         pg_obj = pgen_obj,
    #         student_background = student_goals
    #     )
    #     pg_sb_obj.save()

    # elif json_model_response['function_type'] == 'save_new_note':
    #     note = json_model_response['note'].strip()
    #     pg_note_obj = PythonCourseNote.objects.create(
    #         pg_obj = pgen_obj,
    #         note = note
    #     )
    #     pg_note_obj.save()

    # elif json_model_response['function_type'] == 'update_existing_note':
    #     note_id = json_model_response['note_id']
    #     note_text = json_model_response['note_text'].strip()
        
    #     # TODO: SECURITY RISK --> should also filter for user object
    #     course_note_objects = PythonCourseNote.objects.filter(
    #         id = note_id
    #     )
    #     if len(course_note_objects) == 0:  # TODO: simply going to create new note
    #         pg_note_obj = PythonCourseNote.objects.create(
    #             pg_obj = pgen_obj,
    #             note = note
    #         )
    #         pg_note_obj.save()
        
    #     else:
    #         pg_note_obj = course_note_objects[0]
    #         pg_note_obj.note = note_text
    #         pg_note_obj.save()

    # elif json_model_response['function_type'] == 'save_exercise':
    #     exercise = json_model_response['exercise'].strip()
    #     exercise_obj = PythonCourseExercise.objects.create(
    #         pg_obj = pgen_obj,
    #         exercise = exercise,
    #         complete = False
    #     )
    #     exercise_obj.save()

    # elif json_model_response['function_type'] == 'mark_exercise_complete':
    #     exercise_id = json_model_response['exercise_id'].strip()
    #     exercise_objects = PythonCourseExercise.objects.filter(id = exercise_id)
    #     if len(exercise_objects) == 0:
    #         # TODO: what should be done here?
    #         logging.error(f"For user: {custom_user_obj_id}, the exercise id: {exercise_id} from GPT did not find any corresponding exercise object.")
    #         pass
    #     else:
    #         exercise_obj = exercise_objects[0]
    #         exercise_obj.complete = True
    #         exercise_obj.save()

    # elif json_model_response['function_type'] == 'no_function_needed':
    #     pass

    # json_string_representation = str(json_model_response)
    # pg_new_cv_obj = PythonCourseConversation.objects.create(
    #     pg_obj = pgen_obj,
    #     question = model_response_dict['question'],
    #     question_prompt = model_response_dict['q_prompt'],
    #     response = json_string_representation
    # )
    # pg_new_cv_obj.save()

    # model_response_dict['pcid'] = pgen_obj.id
    # return JsonResponse({'success': True, 'response': model_response_dict})



