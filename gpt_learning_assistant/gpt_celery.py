import os
from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "gpt_learning_assistant.settings")
app = Celery("django_celery")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()

# python -m celery -A gpt_learning_assistant worker