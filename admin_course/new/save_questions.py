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

for ln in lines:
    ln = ln.strip()
    ln_list = ln.split(' | ')
    question_name = ln_list[0]
    question_text = ln_list[1]
    question_test_cases = ''
    if len(ln_list) > 2:
        question_test_cases = ln_list[2]

    print(f"Question Name: {question_name}")
    print(f"Question Text: {question_text}")
    test_case_list = question_test_cases.split('Test Case')
    new_test_case_list = []
    for tc in test_case_list:
        if tc != '':
            new_tc = tc.strip()
            if new_tc[-1] == ',':
                new_tc = new_tc[:-1]
            print(f"Test Case {new_tc}")
            new_test_case_list.append(new_tc)

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





# ex_ln = lines[0].strip()
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

#         print(f"Test Case {new_tc}")
#         # Test Case 1: Input: Word/Phrase = "racecar" --> Output: Palindrome

# print(f"Question Name: {question_name}")
# print(f"Question Text: {question_text}")
# print(f"Question Test Cases: {question_test_cases}")

