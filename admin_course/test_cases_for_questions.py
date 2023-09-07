import sys
sys.path.append('/Users/rahul/Desktop/gpt_learning_assistant')
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "gpt_learning_assistant.settings")
import django
django.setup()
from learning_assistant.models import *



# TODO: 
    # add test-cases for the questions
    # On submit: 
        # user is shown the feedback from AI along with if testcases passed or not





