import sys
sys.path.append('/Users/rahul/Desktop/gpt_learning_assistant')
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "gpt_learning_assistant.settings")
import django
django.setup()
from learning_assistant.models import *



# TODO: 
    # put more thought into the lessons and 'syllabus' 
        # start with below syllabus
        # regenerate the text-files associated with each lesson
            # have lesson-name and questions in same txt file <-- create both together

titles = [
    'Lesson 1: Variables, Data Types, String Manipulation',
    'Lesson 2: For/While Loops & Booleans & Conditionals (If/Else)',
    'Lesson 3: Strings',
    'Lesson 4: Lists',
    'Lesson 5: Dictionaries',
    'Lesson 6: Functions',
    # 'Lesson 6: Side Projects'
]

# for t in titles:
#     l_obj = Lesson.objects.create(
#         title = t
#     )
#     l_obj.save()

