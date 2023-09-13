import sys
sys.path.append('/Users/rahul/Desktop/code_companion/gpt_learning_assistant')
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "gpt_learning_assistant.settings")
import django
django.setup()
from learning_assistant.models import *

import ast
import json



# TODO: 
    # save all the testcases above in the DB (local)
        # test and ensure all the neq questions work well
    # fix all bugs and ensure good
        # edit the about and push / finalize the prod for this feature
    # prioritize the next eng from there:
        # 'general tutor'
    
lesson_obj_new = Lesson.objects.get(title = 'new_void')

fn = 'preliminary_quest_test_cases.txt'
f = open(fn)
lines = f.readlines()

for ln in lines:
    ln = ln.strip()
    if '|' in ln:
        ln_list = ln.split('|')
        # print(ln_list[-1])
        question_name = ln_list[0].strip()
        # print(question_test_cases)
 
        last_li_val = ln_list[-1].strip()
        last_li_val = last_li_val.replace("\'", "\"")
        # if "output" not in last_li_val:
        #     last_li_val = last_li_val.replace("output", '"output"')
        print(last_li_val)
        question_test_cases = json.loads(last_li_val)
    else:
        question_name = ln
        question_test_cases = None

    if question_test_cases is not None:

        for q_tc in question_test_cases:
            input_st = q_tc['input']
            output_st = q_tc['output']

            print(f"question: {question_name} | input: {str(input_st)} | output: {str(output_st)}")

            lq_obj = LessonQuestion.objects.get(question_name = question_name)

            # lq_tc_obj = LessonQuestionTestCase.objects.create(
            #     lesson_question_obj = lq_obj,
            #     input_param = input_st,
            #     correct_output = output_st
            # )
            # lq_tc_obj.save()


