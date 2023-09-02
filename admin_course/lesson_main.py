import sys
sys.path.append('/Users/rahul/Desktop/gpt_learning_assistant')
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "gpt_learning_assistant.settings")
import django
django.setup()
from learning_assistant.models import *



titles = [
    'Lesson 1: Variables, Data Types, String Manipulation',
    'Lesson 2: Conditionals (If/Else)',
    'Lesson 3: For Loops',
    'Lesson 4: While Loops',
    'Lesson 5: Lists/Dictionaries',
    'Lesson 6: Side Projects'
]

# for t in titles:
#     l_obj = Lesson.objects.create(
#         title = t
#     )
#     l_obj.save()

