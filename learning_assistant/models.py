import uuid
from django.db import models

from acc.models import CustomUser


class ChatConversation(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    question = models.CharField(max_length=3000)
    question_prompt = models.TextField()
    response = models.TextField()
    prompt_token_count = models.IntegerField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

class PlaygroundCode(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_obj = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    code_unique_name = models.CharField(max_length=2000)
    user_code = models.TextField()
    user_code_output = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class PlaygroundConversation(ChatConversation):
    code_obj = models.ForeignKey(PlaygroundCode, on_delete=models.CASCADE)

class UserGeneralTutorParent(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_obj = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

class UserGeneralTutorConversation(ChatConversation):
    parent_obj = models.ForeignKey(UserGeneralTutorParent, on_delete=models.CASCADE, blank=True, null=True)
