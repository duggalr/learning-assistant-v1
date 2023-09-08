import sys
sys.path.append('/Users/rahul/Desktop/gpt_learning_assistant')
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "gpt_learning_assistant.settings")
import django
django.setup()
from learning_assistant.models import *




test_case_files_list = [
    'lesson_1_test_cases.txt'
]

for tc_fp in test_case_files_list:

    with open(tc_fp, "r") as f:
        content = f.read()
        lesson_q = content.split('\n\n')

        for lq in lesson_q:
            full_sentence = lq.strip()

            question_name = full_sentence.split('\n')[0].split(': ')[-1].strip()
            print(f"Question: {question_name}")

            question_test_inputs = full_sentence.split('\n')[1:]
            for q_inp in question_test_inputs:
                q_tc_list = q_inp.split('-->')
                q_inputs, q_output = q_tc_list[0].strip(), q_tc_list[1].strip()
                
                q_input_params = []
                if '|' in q_inputs:
                    for t in q_inputs.split('|'):
                        q_input_params.append(t.strip())
                else:
                    q_input_params = [q_inputs.strip()]
                

                q_input_params_st = ', '.join(q_input_params)

                associated_lq_object =  LessonQuestion.objects.get(question_name = question_name)
                print(f"Input: {q_input_params_st} | Output: {q_output} | Obj: {associated_lq_object}")

                # lq_tc_obj = LessonQuestionTestCase.objects.create(
                #     lesson_question_obj = associated_lq_object,
                #     input_param = q_input_params_st,
                #     correct_output = q_output
                # )
                # lq_tc_obj.save()






# test_case_files_list = [
#     ['lesson_1_desc.txt', 'lesson_1_questions.txt', 'less_1_test_cases.txt']
# ]


# for li in test_case_files_list:

#     lesson_desc_fp, lesson_questions_fp, tc_fp = li[0], li[1], li[2]

#     # lesson_desc = open(lesson_desc_fp).read()
#     # lesson_desc_list = lesson_desc.split('Description:')
#     # lesson_name, lesson_desc_text = lesson_desc_list[0].strip(), lesson_desc_list[1].strip()

#     # print(lesson_name, lesson_desc_text)

#     # l_obj = Lesson.objects.create(
#     #     title = lesson_name,
#     #     description = lesson_desc_text
#     # )
#     # l_obj.save()

#     # question_qid_dict = {}
#     # with open(lesson_questions_fp, "r") as f:
#     #     content = f.read()
#     #     lesson_q = content.split('\n\n')

#     #     for lq in lesson_q:
#     #         full_sentence = lq.strip()
#     #         # print(full_sentence)
 
#     #         question_name = full_sentence.split('\n')[0].split(': ')[-1].strip()
#     #         print(question_name, full_sentence)

#     #         lq_obj = LessonQuestion.objects.create(
#     #             question_name = question_name,
#     #             question_text = full_sentence,
#     #             lesson_obj = l_obj
#     #         )
#     #         lq_obj.save()

#     #         question_qid_dict[question_name] = lq_obj

#     test_cases = open(tc_fp).read()
#     with open(lesson_questions_fp, "r") as f:
#         content = f.read()
#         lesson_q = content.split('\n\n')

#         for lq in lesson_q:
#             full_sentence = lq.strip()
#             # print(full_sentence)
 
#             question_name = full_sentence.split('\n')[0].split(': ')[-1].strip()
#             question_test_inputs = full_sentence.split('\n')[1:].strip()
#             for q_inp in question_test_inputs:
#                 q_tc_list = q_inp.split('-->')
#                 q_inputs, q_output = q_tc_list[0].strip(), q_tc_list[1].strip()
                
#                 q_input_params = []
#                 if '|' in q_inputs:
#                     for t in q_inputs.split('|'):
#                         q_input_params.append(t.strip())
#                 else:
#                     q_input_params = [q_inputs.strip()]

#                 associated_lq_object = question_qid_dict[question_name]
#                 lq_tc_obj = LessonQuestionTestCase.objects.create(
#                     lesson_question_obj = associated_lq_object,
#                     input_param_list = q_input_params,
#                     correct_output = q_output
#                 )
#                 lq_tc_obj.save()

