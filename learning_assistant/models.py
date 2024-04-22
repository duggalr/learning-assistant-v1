import uuid
from django.db import models

from acc.models import CustomUser


## Playground + General Tutor Chat ##

class ChatConversation(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    question = models.CharField(max_length=3000)
    question_prompt = models.TextField()
    response = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

class PlaygroundCode(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_obj = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    code_unique_name = models.CharField(max_length=2000)
    user_code = models.TextField()
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


## Python Course Gen ##

class PythonCourseParent(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_obj = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

class PythonCourseModuleParent(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    pg_obj = models.ForeignKey(PythonCourseParent, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class PythonCourseConversation(ChatConversation):
    pg_obj = models.ForeignKey(PythonCourseParent, on_delete=models.CASCADE)

# class PythonCourseStudentBackground(PythonCourseModuleParent):  # TODO: delete this model
#     student_background = models.TextField()

class PythonCourseNote(PythonCourseModuleParent):
    note = models.TextField()

class PythonCourseExercise(PythonCourseModuleParent):
    exercise = models.TextField()
    complete = models.BooleanField(default=False)
    completed_at = models.DateTimeField(auto_now=True)

class PythonCourseStudentOutline(PythonCourseModuleParent):
    # json_response = models.TextField()
    student_background = models.TextField(blank=True, null=True)
    course_name = models.TextField(blank=True, null=True)
    course_description = models.TextField(blank=True, null=True)
    module_list = models.TextField(blank=True, null=True)

class PythonCourseStudentModuleChild(models.Model):
    std_outline_obj = models.ForeignKey(PythonCourseStudentOutline, on_delete=models.CASCADE)
    module_number = models.IntegerField()
    module_topic = models.TextField()
    module_description = models.TextField()
