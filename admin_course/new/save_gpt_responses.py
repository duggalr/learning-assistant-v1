import sys
sys.path.append('/Users/rahul/Desktop/code_companion/gpt_learning_assistant')
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "gpt_learning_assistant.settings")
import django
django.setup()
from learning_assistant.old_models import *

import ast
import json



# lesson_obj_new = Lesson.objects.create(
#     title = 'new_void'
# )
# lesson_obj_new.save()

# fn = 'prompt_response_1_6.txt'
# f = open(fn)
# lines = f.read()


# base_dir = '/Users/rahul/Desktop/code_companion/gpt_learning_assistant/admin_course/new'
# files = os.listdir(base_dir)

# prompt_response_files = [os.path.join(base_dir, fn) for fn in files if 'prompt_response_' in fn]
# prompt_response_files.sort()
# for p_fn in prompt_response_files:
#     print(p_fn)



lesson_obj_new = Lesson.objects.create(
    title = 'new_void'
)
lesson_obj_new.save()

base_name = 'prompt_response_'
for idx in range(0, 45, 5):
    fn = base_name + str(idx) + '_' + str((idx+5)) + '.txt'
    print(f"On File: {fn}")

    # f = open(fn)
    # data = json.load(f)
    # print(data)
    # print()

    f = open(fn)
    data = f.read()
    fmt_data = ast.literal_eval(data)
    for tmp_di in fmt_data:
        question_name = tmp_di['question_name'].strip()
        question_text = tmp_di['question_text'].strip()
        question_test_cases = tmp_di['question_test_cases']
        
        print(f"Question: {question_name} | Text: {question_text}")
        
        # lq_obj = LessonQuestion.objects.create(
        #     question_name = question_name, 
        #     question_text = question_text,
        #     lesson_obj = lesson_obj_new
        # )
        # lq_obj.save()

        # print(f"Question: {question_name} | Text: {question_text}")
        # for tc_list in question_test_cases:
        #     input_txt = tc_list['input']
        #     output_txt = tc_list['output']

        #     # print(input_txt)
        #     # print(output_txt)
        #     # print()

        #     if type(input_txt) == dict:
        #         input_txt_st = ', '.join([str(input_txt[k]) for k in input_txt])
        #     else:
        #         input_txt_st = input_txt

        #     if type(output_txt) == dict:
        #         output_txt_st = ', '.join([str(output_txt[k]) for k in output_txt])
        #     else:
        #         output_txt_st = output_txt

        #     # print(f"{input_txt_st} | {output_txt_st}")
        #     # print()

        #     lq_tc_obj = LessonQuestionTestCase.objects.create(
        #         lesson_question_obj = lq_obj,
        #         input_param = input_txt_st,
        #         correct_output = output_txt_st
        #     )
        #     lq_tc_obj.save()




# f = open(fn)
# data = json.load(f)
# # print(data)
# for qn in data:
#     qn_dict = data[qn]
#     question_name = qn.strip()
#     question_text = qn_dict['question_text'].strip()
#     question_test_cases = qn_dict['test_cases']
    
#     print(f"Question: {question_name} | Text: {question_text}")
#     for tc_list in question_test_cases:
#         input_txt = tc_list['input']
#         output_txt = tc_list['output']

#         if type(input_txt) == dict:
#             input_txt_st = ', '.join([str(input_txt[k])
#                                        for k in input_txt])
#         else:
#             input_txt_st = input_txt

#         print(f"{input_txt} | {input_txt_st} | {output_txt}")



# TODO: 
    # save this input
        # should it be a dict for input?
            # determine and go from there

            # books / wealthsimple


