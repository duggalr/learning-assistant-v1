from django.db import models

# Create your models here.


class UserOAuth(models.Model):
    auth_type = models.CharField(max_length=500)
    email = models.EmailField()
    email_verified = models.BooleanField()
    name = models.TextField()
    created_at = models.IntegerField()
    updated_at = models.IntegerField()


class UserCode(models.Model):
    user_auth_obj = models.ForeignKey(UserOAuth, on_delete=models.CASCADE, blank=True, null=True)
    code_unique_name = models.CharField(max_length=2000)
    user_code = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)


class UserConversation(models.Model):
    user_auth_obj = models.ForeignKey(UserOAuth, on_delete=models.CASCADE, blank=True, null=True)
    code_obj = models.ForeignKey(UserCode, on_delete=models.CASCADE)
    question = models.CharField(max_length=3000)
    question_prompt = models.TextField()
    response = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)


class Lesson(models.Model):
    title = models.CharField(max_length=3000)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)


class LessonQuestion(models.Model):
    # TODO: add tags for each question 
    question_name = models.CharField(max_length=3000)
    question_text = models.TextField()
    lesson_obj = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

