import ast
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse

from .models import *

# from acc.models import CustomUser, AnonUser
from .scripts import utils, open_ai_utils
from .scripts.personal_course_gen import a_student_description_generation_new, b_student_course_outline_generation_new, c_student_course_note_generation_new, d_student_course_note_quiz_generation, bing_search_new



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
        general_tutor_parent_obj_id = request.POST['general_tutor_parent_obj_id']
        user_message = request.POST['message'].strip()

        # TODO: passing user-obj-id directly proposes security-vuln <-- **FIX**
        custom_user_objects = CustomUser.objects.filter(id = custom_user_obj_id)
        if len(custom_user_objects) == 0:
            return JsonResponse({'success': False, 'response': 'User not found.'})

        custom_user_obj = custom_user_objects[0]

        
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
                chat_parent_object = parent_chat_obj
            ).order_by('-created_at')

            if len(past_conversation_objects) > 0:
                prev_conversation_history = []
                for uc_tut_obj in past_conversation_objects:
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

        # TODO: test and finalize to ensure this works
        uct_obj = UserGeneralTutorConversation.objects.create(
            chat_parent_object = parent_chat_obj,
            question = model_response_dict['student_response'],
            question_prompt = model_response_dict['q_prompt'],
            response = model_response_dict['response']
        )
        uct_obj.save()
        
        # model_response_dict['uct_parent_obj_id'] = ugt_parent_obj.id
        model_response_dict['uct_parent_obj_id'] = parent_chat_obj.id
        return JsonResponse({'success': True, 'response': model_response_dict})


### Course Gen ###

def course_generation_background_chat(request):
    # # TODO: 
    #     # for anon, fetch the user object and the conv-obj if any
    #     # pass as hidden input id and go from there
    
    custom_user_obj = utils._get_customer_user(request)
    anon_user = utils._check_if_anon_user(custom_user_obj)

    # course_gen_bg_parent_objects = CourseGenBackgroundParent.objects.filter(
    #     user_obj = custom_user_obj
    # )

    # # TODO: only using this for anno user
    # course_gen_obj = None
    # if len(course_gen_bg_parent_objects) > 0 and custom_user_obj.anon_user:
    #     course_gen_obj = course_gen_bg_parent_objects[0]

    # user_conversation_objects = CourseGenBackgroundConversation.objects.filter(
    #     bg_parent_obj = course_gen_obj
    # ).order_by('created_at')

    return render(request, 'personal_course_gen/student_background_chat.html', {
        'anon_user': anon_user,
        'custom_user_obj': custom_user_obj,
        'custom_user_obj_id': custom_user_obj.id,
        # 'course_gen_bg_parent_obj': course_gen_obj,
        # 'current_conversation_list': user_conversation_objects
    })


def handle_course_generation_background_message(request):
        
    if request.method == 'POST':
        print('cs-chat-data:', request.POST)

        custom_user_obj_id = request.POST['custom_user_object_id']
        course_gen_bg_parent_object = request.POST['bg_parent_obj_id']
        user_message = request.POST['message'].strip()
        
        custom_user_objects = CustomUser.objects.filter(id = custom_user_obj_id)
        if len(custom_user_objects) == 0:
            return JsonResponse({'success': False, 'response': 'User not found.'})
        
        custom_user_obj = custom_user_objects[0]
        cg_bg_parent_obj = None
        prev_conversation_st = ''
        if course_gen_bg_parent_object == '':
            cg_bg_parent_obj = CourseGenBackgroundParent.objects.create(
                user_obj = custom_user_obj
            )
        else:
            cg_bg_parent_objects = CourseGenBackgroundParent.objects.filter(
                user_obj = custom_user_obj,
                id = course_gen_bg_parent_object
            )
            if len(cg_bg_parent_objects) > 0:
                cg_bg_parent_obj = cg_bg_parent_objects[0]
            else:
                return JsonResponse({'success': False, 'response': 'Object not found.'})

            past_conv_objects = CourseGenBackgroundConversation.objects.filter(
                bg_parent_obj = cg_bg_parent_obj
            )

            prev_conversation_history = []
            for uc_tut_obj in past_conv_objects:
                uc_question = uc_tut_obj.question
                uc_response = uc_tut_obj.response
                prev_conversation_history.append(f"Question: { uc_question }")
                prev_conversation_history.append(f"Response: { uc_response }")

            prev_conversation_st = '\n'.join(prev_conversation_history).strip()
            # print('PREVIOUS CONV:', prev_conversation_st)

        # op_ai_wrapper = open_ai_utils.OpenAIWrapper()
        # model_response_dict = op_ai_wrapper.handle_course_generation_message(
        #     student_response = user_message,
        #     previous_chat_history = prev_conversation_st,
        # )

        model_response_dict = a_student_description_generation_new.generate_answer(
            student_response = user_message, 
            prev_chat_history = prev_conversation_st
        )

        model_response_json = model_response_dict['response']
        model_response_final_message = model_response_json['final_message']
        model_response_message_str = model_response_json['response'].strip()

        # TODO: continue the conversation
        if model_response_final_message is False:
            course_bg_conv_obj = CourseGenBackgroundConversation.objects.create(
                bg_parent_obj = cg_bg_parent_obj,
                question = user_message,
                question_prompt = model_response_dict['q_prompt'],
                response = model_response_message_str
            )
            course_bg_conv_obj.save()

            model_response_dict['course_gen_parent_obj_id'] = cg_bg_parent_obj.id
            return JsonResponse({'success': True, 'final_message': False, 'response': model_response_dict})

        else:
            
            cg_bg_parent_obj.final_response = model_response_message_str
            cg_bg_parent_obj.save()

            print("GENERATING THE COURSE OUTLINE...")

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

            # Bing Results
            bing_course_outline_query = initial_student_course_name
            bing_results_rv = bing_search_new.get_bing_results(
                query = bing_course_outline_query,
                k = 8
            )

            ucourse_obj = UserCourse.objects.create(
                initial_background_object = cg_bg_parent_obj,
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

            for bg_rs_dict in bing_results_rv:
                cm_br_obj = UserCourseModulesBingResult.objects.create(
                    parent_course_object = ucourse_obj,
                    name = bg_rs_dict['name'],
                    url = bg_rs_dict['url'],
                    snippet = bg_rs_dict['snippet'],
                )
                cm_br_obj.save()

            return JsonResponse({'success': True, 'response': model_response_dict, 'final_message': True, 'new_course_object_id': ucourse_obj.id})



def student_course_outline(request, cid):
    
    # all_course_objects = UserCourse.objects.all().order_by('-created_at')
    # course_object = all_course_objects[0]

    course_object = get_object_or_404(UserCourse, id = cid)
 
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

    bing_result_objects = UserCourseModulesBingResult.objects.filter(parent_course_object = course_object)

    # TODO: 
    return render(request, 'personal_course_gen/student_course_outline.html', {
        'course_object': course_object,
        'course_module_list': course_module_list_rv,
        'user_conversation_objects': user_conversation_rv,
        'bing_result_objects': bing_result_objects
    })


def student_course_homepage(request, cid):
    # TODO:
        # pass in the course id and display the course along with generate notes/exercise button
        # handle all functionality here

    custom_user_obj = utils._get_customer_user(request)
    anon_user = utils._check_if_anon_user(custom_user_obj)

    course_object = get_object_or_404(UserCourse, id = cid)
    # all_course_objects = UserCourse.objects.all().order_by('-created_at')
    # course_object = all_course_objects[0]

    course_module_list = UserCourseModules.objects.filter(
        parent_course_object = course_object
    ).order_by('module_number')

    course_module_list_rv = []
    for md_obj in course_module_list:
        c_md_note_objects = UserCourseModuleNote.objects.filter(
            course_module_object = md_obj
        )
        c_md_note_obj = None
        if len(c_md_note_objects) > 0:
            c_md_note_obj = c_md_note_objects[0]
        
        course_module_list_rv.append([md_obj, ast.literal_eval(md_obj.module_description), c_md_note_obj])
    
    bing_result_objects = UserCourseModulesBingResult.objects.filter(parent_course_object = course_object)

    return render(request, 'personal_course_gen/course_homepage.html', {
        'custom_user_obj': custom_user_obj,
        'custom_user_obj_id': custom_user_obj.id,
        'course_object': course_object,
        'course_module_list': course_module_list_rv,
        'bing_result_objects': bing_result_objects
    })


def all_student_courses(request):
    # initial_user_session = request.session.get("user")    
    # user_oauth_obj = UserOAuth.objects.get(email = initial_user_session['userinfo']['email'])
    
    custom_user_obj = utils._get_customer_user(request)
    anon_user = utils._check_if_anon_user(custom_user_obj)

    user_course_objects = UserCourse.objects.filter(
        initial_background_object__user_obj = custom_user_obj
    ).order_by('-updated_at')

    return render(request, 'personal_course_gen/new_course_all_list.html', {
        'user_course_objects': user_course_objects,
    })


# TODO: complete this and finalize/test from there; when rafctoring and furhter changes, make new branch 
def generate_module_notes(request):

    if request.method == 'POST':
        print('cs-chat-data:', request.POST)

        custom_user_obj_id = request.POST['custom_user_object_id']
        # course_gen_bg_parent_object = request.POST['bg_parent_obj_id']
        course_module_object_id = request.POST['module_object_id']
        # student_response = request.POST['student_response'].strip()

        custom_user_objects = CustomUser.objects.filter(id = custom_user_obj_id)
        if len(custom_user_objects) == 0:
            return JsonResponse({'success': False, 'response': 'User not found.'})
        
        custom_user_obj = custom_user_objects[0]

        c_module_objects = UserCourseModules.objects.filter(
            id = course_module_object_id
        )
        if len(c_module_objects) == 0:
            return JsonResponse({'success': False, 'message': "Module not found."})

        c_module_obj = c_module_objects[0]
        student_background_info = c_module_obj.parent_course_object.initial_background_object.final_response

        course_outline_str = c_module_obj.parent_course_object.module_list
        course_outline_dict = ast.literal_eval(course_outline_str)
        course_outline_final_str = ""
        for mdi in course_outline_dict:
            md_full_name = f"Module #{mdi['module_number']}: {mdi['module_topic']}\n"
            md_description_str = '\n'.join(mdi['module_description'])
            mstr = md_full_name + '\n' + md_description_str + '\n'
            course_outline_final_str += mstr
        
        
        module_course_note_objects = UserCourseModuleNote.objects.filter(
            course_module_object = course_module_object_id
        )
        if len(module_course_note_objects) == 0:
            course_module_notes_str = ""
        else:
            course_module_notes_str = module_course_note_objects[0].notes_md
        current_module_info = f"Module #{c_module_obj.module_number}: {c_module_obj.module_topic}\n{'\n'.join(c_module_obj.module_description)}"

        current_module_note_response_dict = c_student_course_note_generation_new.generate_course_notes(
            student_info = student_background_info,
            course_outline = course_outline_final_str,
            current_module_information = current_module_info,
            current_week_course_notes = course_module_notes_str,
            student_response = '',
            previous_conversation_history = '',
        )

        current_module_note_response_json = current_module_note_response_dict['response']
        cn_generation = current_module_note_response_json['course_note_generation']

        if cn_generation:

            UserCourseModuleNote.objects.filter(course_module_object = course_module_object_id).delete()

            course_notes_text = current_module_note_response_json['course_notes'].strip()
            uc_md_note_obj = UserCourseModuleNote.objects.create(
                course_module_object = c_module_obj,
                notes_md = course_notes_text
            )
            uc_md_note_obj.save()

            quiz_note_response_dict = d_student_course_note_quiz_generation.generate_quiz(
                student_info = student_background_info,
                course_notes = course_notes_text,
            )

            quiz_response_json_list = quiz_note_response_dict['response']['quiz']
            for qdi in quiz_response_json_list:
                md_question_obj = UserCourseModuleNoteQuestion.objects.create(
                    course_note_object = uc_md_note_obj,
                    question_number = qdi['question_number'],
                    question = qdi['question'],
                    multiple_choice_options = qdi['multiple_choice_options'],
                    answer = qdi['answer'],
                )
                md_question_obj.save()

        else:
            uc_md_note_obj = UserCourseModuleNote.objects.get(course_module_object = c_module_obj)


        uc_md_cv_obj = UserCourseModuleConversation.objects.create(
            course_module_object = c_module_obj,
            question = '',
            question_prompt = current_module_note_response_dict['q_prompt'],
            response = current_module_note_response_dict['response']['model_response']
        )
        uc_md_cv_obj.save()
        
        return JsonResponse({'success': True, 'module_note_obj_id': uc_md_note_obj.id})


def course_module_notes_view(request, mid):

    custom_user_obj = utils._get_customer_user(request)
    anon_user = utils._check_if_anon_user(custom_user_obj)

    course_module_obj = get_object_or_404(UserCourseModuleNote, id = mid)

    note_quiz_question_objects = UserCourseModuleNoteQuestion.objects.filter(
        course_note_object = course_module_obj
    ).order_by('question_number')

    note_quiz_objects_list = []
    for qz_obj in note_quiz_question_objects:
        mc_option_list = ast.literal_eval(qz_obj.multiple_choice_options)
        note_quiz_objects_list.append([qz_obj, mc_option_list])

    return render(request, 'personal_course_gen/course_module_note_view.html', {        
        'anon_user': anon_user,
        'custom_user_obj': custom_user_obj,
        'custom_user_obj_id': custom_user_obj.id,

        'course_obj': course_module_obj.course_module_object.parent_course_object,
        'module_note_obj': course_module_obj,
        # 'quiz_questions': note_quiz_question_objects
        'quiz_questions': note_quiz_objects_list
    })











    #     initial_user_session = request.session.get('user')
    #     user_oauth_obj = UserOAuth.objects.get(email = initial_user_session['userinfo']['email'])
        
    #     course_module_object_id = request.POST['module_object_id']
    #     student_response = request.POST['student_response']

    #     prev_conversation_history = ''
    #     past_user_conversation_objects = UserCourseModuleConversation.objects.filter(course_module_object = course_module_object_id)
    #     prev_conversation_history = []
    #     for uc_obj in past_user_conversation_objects[:3]:
    #         uc_question = uc_obj.question
    #         uc_response = uc_obj.response
    #         prev_conversation_history.append(f"Question: { uc_question }")
    #         prev_conversation_history.append(f"Response: { uc_response }")

    #     prev_conversation_st = '\n'.join(prev_conversation_history).strip()

    #     c_module_objects = UserCourseModules.objects.filter(
    #         id = course_module_object_id
    #     )
    #     if len(c_module_objects) == 0:
    #         return JsonResponse({'success': False, 'message': "Module not found."})
        
    #     c_module_obj = c_module_objects[0]

    #     module_name = f"Module #{c_module_obj.module_number}: {c_module_obj.module_topic}"
    #     module_desc_list = ast.literal_eval(c_module_obj.module_description)
    #     module_desc_full_str = '\n'.join(module_desc_list)
        
    #     # UserCourseModuleNote
    #     # UserCourseModuleConversation

    #     student_background_info = c_module_obj.parent_course_object.initial_background_object.final_response
        
    #     course_outline_str = c_module_obj.parent_course_object.module_list
    #     course_outline_dict = ast.literal_eval(course_outline_str)
    #     course_outline_final_str = ""
    #     for mdi in course_outline_dict:
    #         md_full_name = f"Module #{mdi['module_number']}: {mdi['module_topic']}\n"
    #         md_description_str = '\n'.join(mdi['module_description'])
    #         mstr = md_full_name + '\n' + md_description_str + '\n'
    #         course_outline_final_str += mstr
        
        
    #     module_course_note_objects = UserCourseModuleNote.objects.filter(
    #         course_module_object = course_module_object_id
    #     )
    #     if len(module_course_note_objects) == 0:
    #         course_module_notes_str = ""
    #     else:
    #         course_module_notes_str = module_course_note_objects[0].notes_md

    #     current_module_info = f"Module #{c_module_obj.module_number}: {c_module_obj.module_topic}\n{'\n'.join(c_module_obj.module_description)}"
        
    #     current_module_note_response_dict = c_student_course_note_generation_new.generate_course_notes(
    #         student_info = student_background_info,
    #         course_outline = course_outline_final_str,
    #         current_module_information = current_module_info,
    #         current_week_course_notes = course_module_notes_str,
    #         student_response = student_response,
    #         previous_conversation_history = prev_conversation_st,
    #     )

    #     current_module_note_response_json = current_module_note_response_dict['response']
        
    #     cn_generation = current_module_note_response_json['course_note_generation']
    #     if cn_generation:

    #         UserCourseModuleNote.objects.filter(course_module_object = course_module_object_id).delete()

    #         course_notes_text = current_module_note_response_json['course_notes'].strip()
    #         uc_md_note_obj = UserCourseModuleNote.objects.create(
    #             course_module_object = c_module_obj,
    #             notes_md = course_notes_text
    #         )
    #         uc_md_note_obj.save()

    #         quiz_note_response_dict = d_student_course_note_quiz_generation.generate_quiz(
    #             student_info = student_background_info,
    #             course_notes = course_notes_text,
    #         )

    #         quiz_response_json_list = quiz_note_response_dict['response']['quiz']
    #         for qdi in quiz_response_json_list:
    #             md_question_obj = UserCourseModuleNoteQuestion.objects.create(
    #                 course_note_object = uc_md_note_obj,
    #                 question_number = qdi['question_number'],
    #                 question = qdi['question'],
    #                 multiple_choice_options = qdi['multiple_choice_options'],
    #                 answer = qdi['answer'],
    #             )
    #             md_question_obj.save()

    #     else:
    #         uc_md_note_obj = UserCourseModuleNote.objects.get(course_module_object = c_module_obj)

    #     uc_md_cv_obj = UserCourseModuleConversation.objects.create(
    #         user_auth_obj = user_oauth_obj,
    #         course_module_object = c_module_obj,
    #         question = student_response,
    #         question_prompt = current_module_note_response_dict['q_prompt'],
    #         response = current_module_note_response_dict['response']['model_response']
    #     )
    #     uc_md_cv_obj.save()
        
    #     return JsonResponse({'success': True, 'module_note_obj_id': uc_md_note_obj.id})













    
    # # if request.method == 'POST':

    # #     custom_user_obj_id = request.POST['custom_user_obj_id']
    # #     user_question = request.POST['message'].strip()
    # #     bg_chat_parent_obj_id = request.POST['bg_parent_obj_id']

    # #     custom_user_objects = CustomUser.objects.filter(id = custom_user_obj_id)
    # #     if len(custom_user_objects) == 0:
    # #         return JsonResponse({'success': False, 'response': 'User not found.'})

    # #     custom_user_obj = custom_user_objects[0]

    # #     cg_bg_parent_obj = None
    # #     if bg_chat_parent_obj_id == 'None':
    # #         cg_bg_parent_obj = CourseGenBackgroundParent.objects.create(
    # #             custom_user_obj = custom_user_obj
    # #         )
    # #     else:
    # #         cg_bg_parent_objects = CourseGenBackgroundParent.objects.filter(
    # #             user_obj = custom_user_obj,
    # #             id = bg_chat_parent_obj_id
    # #         )
    # #         if len(cg_bg_parent_objects) > 0:
    # #             cg_bg_parent_obj = cg_bg_parent_objects[0]
    # #         else:
    # #             return JsonResponse({'success': False, 'response': 'Object not found.'})

    # #     student_background_full_conversation_list = []
    # #     past_conv_objects = CourseGenBackgroundConversation.objects.filter(
    # #         user_obj = custom_user_obj,
    # #         bg_parent_obj = cg_bg_parent_obj
    # #     )
        
    # #     prev_conversation_history = []
    # #     for uc_tut_obj in past_conv_objects:
    # #         uc_question = uc_tut_obj.question
    # #         uc_response = uc_tut_obj.response
    # #         prev_conversation_history.append(f"Question: { uc_question }")
    # #         prev_conversation_history.append(f"Response: { uc_response }")

    # #     prev_conversation_st = '\n'.join(prev_conversation_history).strip()

    # #     print('PREVIOUS CONV:', prev_conversation_st)

    # #     op_ai_wrapper = open_ai_utils.OpenAIWrapper()
    # #     model_response_dict = op_ai_wrapper.handle_course_generation_message(
    # #         student_response = user_question,
    # #         previous_chat_history = prev_conversation_st,

    # #     )

    # #     course_bg_conv_obj = CourseGenBackgroundConversation.objects.create(
    # #         bg_parent_obj = bg_chat_parent_obj_id,
    # #         user_obj = custom_user_obj,
    # #         question = user_question,
    # #         question_prompt = model_response_dict['q_prompt'],
    # #         response = model_response_dict['response']
    # #     )
    # #     course_bg_conv_obj.save()





