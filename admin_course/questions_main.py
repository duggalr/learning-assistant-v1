import sys
sys.path.append('/Users/rahul/Desktop/gpt_learning_assistant')
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "gpt_learning_assistant.settings")
import django
django.setup()
from learning_assistant.models import *



# q_files_list = [
#     # 'questions_p1.txt',
#     # 'questions_p2.txt',
#     ## TODO: need to name the questions in the files below 
#     # 'questions_p3.txt',
#     # 'questions_p4.txt',
#     # 'questions_p5.txt',
#     # 'questions_p6.txt',
# ]

q_files_list = [
    ['lesson_1_desc.txt', 'lesson_1_questions.txt'],
    ['lesson_2_desc.txt', 'lesson_2_questions.txt'],
    ['lesson_3_desc.txt', 'lesson_3_questions.txt']
]

for li in q_files_list:
    lesson_desc_fp, lesson_questions_fp = li[0], li[1]

    lesson_desc = open(lesson_desc_fp).read()
    lesson_questions = open(lesson_questions_fp).readlines()

    lesson_desc_list = lesson_desc.split('Description:')
    lesson_name, lesson_desc_text = lesson_desc_list[0].strip(), lesson_desc_list[1].strip()

    print(lesson_name, lesson_desc_text)

    # l_obj = Lesson.objects.create(
    #     title = lesson_name,
    #     description = lesson_desc_text
    # )
    # l_obj.save()

    # for lq in lesson_questions:
    #     full_sentence = lq.strip()
    #     tmp_li = full_sentence.split(': ')
    #     print(tmp_li)
    #     question_name = tmp_li[0].strip()
    #     question_text = tmp_li[1].strip()

    #     lq_obj = LessonQuestion.objects.create(
    #         question_name = question_name,
    #         question_text = question_text,
    #         lesson_obj = l_obj
    #     )
    #     lq_obj.save()

