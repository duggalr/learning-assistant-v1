import sys
sys.path.append('/Users/rahul/Desktop/code_companion/gpt_learning_assistant')
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "gpt_learning_assistant.settings")
import django
django.setup()

from learning_assistant.models import PythonCourseLesson, PythonLessonQuestion



# lesson_zero_title = 'Lesson 1: Variables, Data Types (Strings, Integers, Floats, Boolean), Operators, User Input'
# lesson_zero_description = 'This lesson covers the absolute foundations of Python, covering variables, print statements, common data types, and user inputs.'

lesson_one_title = 'Lesson 1: Introduction to Functions'
lesson_one_description = 'This lesson introduces the concept of functions, parameters, and return statements.'
lesson_video_url = 'https://www.youtube.com/embed/tgbNymZ7vqY'  # TODO: this must be an embed url
# pc_lesson_obj = PythonCourseLesson.objects.create(
#     lesson_title = lesson_one_title,
#     lesson_description = lesson_one_description,
#     lesson_video = lesson_video_url
# )
# pc_lesson_obj.save()


