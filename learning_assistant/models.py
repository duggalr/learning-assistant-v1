import uuid
from django.db import models
# from django.utils import timezone

from acc.models import CustomUser


class PlaygroundCode(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_obj = models.ForeignKey(CustomUser)
    code_unique_name = models.CharField(max_length=2000)
    user_code = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class PlaygroundConversation(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    code_obj = models.ForeignKey(PlaygroundCode, on_delete=models.CASCADE)
    question = models.CharField(max_length=3000)
    question_prompt = models.TextField()
    response = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)


