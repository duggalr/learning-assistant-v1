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
lesson_video_url = 'https://www.youtube.com/embed/tgbNymZ7vqY'
# pc_lesson_obj = PythonCourseLesson.objects.create(
#     lesson_title = lesson_one_title,
#     lesson_description = lesson_one_description,
#     lesson_video = lesson_video_url
# )
# pc_lesson_obj.save()


# lesson_zero_title = 'Lesson 0: Introduction - The Basics'
# lesson_zero_description = 'In this lesson, you will learn the absolute basics of Python, including print statements, variables, common data types, math operations, comments, and getting user input.'
# lesson_video_url = 'https://www.youtube.com/embed/tgbNymZ7vqY'
# pc_lesson_obj = PythonCourseLesson.objects.create(
#     lesson_title = lesson_zero_title,
#     lesson_description = lesson_zero_description,
#     lesson_video = lesson_video_url
# )
# pc_lesson_obj.save()

# Lesson 0: Introduction to Data Types, Operators, and User Input is the starting point for your programming journey. 
# In this lesson, you'll grasp the basics of essential data types like Strings, Integers, Floats, and Booleans, learn how to 
# manipulate data with operators, and discover the art of user input, enabling you to create interactive applications and solve 
# real-world problems. Whether you're a novice or an experienced programmer, this foundational knowledge is key to building practical 
# skills and developing dynamic software.

