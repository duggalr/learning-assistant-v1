

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

    return render(request, 'personal_course_gen/student_course_outline.html', {
        'course_object': course_object,
        'course_module_list': course_module_list_rv,
        'user_conversation_objects': user_conversation_rv,
        'bing_result_objects': bing_result_objects
    })


def handle_student_course_outline_chat_message(request):
    
    # TODO:
    if request.method == "POST":
        
        custom_user_obj = utils._get_customer_user(request)
        anon_user = utils._check_if_anon_user(custom_user_obj)

        parent_course_obj_id = request.POST['course_outline_object_id']

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


def student_course_homepage(request, cid):

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

