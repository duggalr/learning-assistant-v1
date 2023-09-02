import sys
sys.path.append('/Users/rahul/Desktop/gpt_learning_assistant')
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "gpt_learning_assistant.settings")
import django
django.setup()
from learning_assistant.models import *



lesson_obj = Lesson.objects.all()[0]
print('lesson-obj:', lesson_obj.title)

q_one_fp = 'questions_p1.txt'
f = open(q_one_fp)
lines = f.readlines()

# for l in lines[1:]:
#     st = l.strip()
#     tmp_li = st.split(': ')
#     question_name = tmp_li[0].strip()
#     question_text = tmp_li[1].strip()

#     lq_obj = LessonQuestion.objects.create(
#         question_name = question_name,
#         question_text = question_text,
#         lesson_obj = lesson_obj
#     )
#     lq_obj.save()
    

