import sys
sys.path.append('/Users/rahul/Desktop/code_companion/gpt_learning_assistant')
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "gpt_learning_assistant.settings")
import django
django.setup()
from learning_assistant.models import *


fp = 'preliminary_questions.txt'
f = open(fp)
lines = f.readlines()

lesson_obj_new = Lesson.objects.create(
    title = 'new_void'
)
lesson_obj_new.save()

for ln in lines:
    ln = ln.strip()
    ln_list = ln.split(' | ')
    question_name = ln_list[0].strip()
    question_text = ln_list[1].strip()
    question_test_cases = ''
    if len(ln_list) > 2:
        question_test_cases = ln_list[2]

    print(f"Question Name: {question_name}")
    print(f"Question Text: {question_text}")
    # test_case_list = question_test_cases.split('Test Case')
    # new_test_case_list = []
    # for tc in test_case_list:
    #     if tc != '':
    #         new_tc = tc.strip()
    #         if new_tc[-1] == ',':
    #             new_tc = new_tc[:-1]
            
    #         print(f"Test Case {new_tc}")
    #         print(f"Question: {question_name} | Question Text: {question_text} | Test Case {new_tc}")
    #         new_test_case_list.append(new_tc)

    # for tc_txt in new_test_case_list:
    #     print(f"{tc_txt}")

    lq_obj = LessonQuestion.objects.create(
        question_name = question_name, 
        question_text = question_text,
        lesson_obj = lesson_obj_new
    )
    lq_obj.save()

    

    # for tc in new_test_case_list:
    #     lq_tc_obj = LessonQuestionTestCase.objects.create(
    #         lesson_question_obj = lq_obj,
    #         test_case_full_text = tc
    #     )
    #     lq_tc_obj.save()



    # npc_q_obj = NewPracticeQuestion.objects.create(
    #     question_name = question_name,
    #     question_text = question_text
    # )
    # npc_q_obj.save()

    # for tc in new_test_case_list:
    #     npc_tc_obj = NewPracticeTestCase.objects.create(
    #         question_obj = npc_q_obj,
    #         test_case_text = tc
    #     )
    #     npc_tc_obj.save()





# ex_ln = lines[31].strip()
# ex_ln_list = ex_ln.split(' | ')
# question_name = ex_ln_list[0]
# question_text = ex_ln_list[1]
# question_test_cases = ''
# if len(ex_ln_list) > 2:
#     question_test_cases = ex_ln_list[2]

# test_case_list = question_test_cases.split('Test Case')
# for tc in test_case_list:
#     if tc != '':
#         new_tc = tc.strip()
#         if new_tc[-1] == ',':
#             new_tc = new_tc[:-1]

#         # print(f"Test Case {new_tc}")
#         new_tc_list = new_tc.split(': ')
#         input_param = new_tc_list[2].split(' --> ')[0].strip()
#         output_param = new_tc_list[-1].strip()
#         print(f"input: {input_param}")
#         print(f"output: {output_param}")

#         # Test Case 1: Input: Word/Phrase = "racecar" --> Output: Palindrome

# # print(f"Question Name: {question_name}")
# # print(f"Question Text: {question_text}")
# # print(f"Question Test Cases: {question_test_cases}")

