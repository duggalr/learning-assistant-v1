import uuid
from django.db import models
# from django.utils import timezone

from acc.models import CustomUser



class ChatConversation(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # user_auth_obj = models.ForeignKey(UserOAuth, on_delete=models.CASCADE, blank=True, null=True)
    # user_obj = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
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
    # id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_obj = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

class UserGeneralTutorConversation(models.Model):
    chat_parent_object = models.ForeignKey(UserGeneralTutorParent, on_delete=models.CASCADE, blank=True, null=True)
    question = models.CharField(max_length=3000)
    question_prompt = models.TextField()
    response = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)



### Course Generation ###

class CourseGenBackgroundParent(models.Model):
    user_obj = models.ForeignKey(CustomUser, on_delete=models.CASCADE, blank=True, null=True)
    final_response = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class CourseGenBackgroundConversation(ChatConversation):
    bg_parent_obj = models.ForeignKey(CourseGenBackgroundParent, on_delete=models.CASCADE, blank=True, null=True)

# class UserBackgroundParent(ChatParent):
#     final_response = models.TextField(blank=True, null=True)

class UserCourse(models.Model):
    initial_background_object = models.ForeignKey(CourseGenBackgroundParent, on_delete=models.CASCADE, blank=True, null=True)
    name = models.CharField(max_length=3000)
    description = models.TextField()
    module_list = models.TextField()
    # outline = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class UserCourseModules(models.Model):
    parent_course_object = models.ForeignKey(UserCourse, on_delete=models.CASCADE, blank=True, null=True)
    module_number = models.IntegerField(blank=True, null=True)
    module_topic = models.TextField()
    module_description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

class UserCourseModulesBingResult(models.Model):
    parent_course_object = models.ForeignKey(UserCourse, on_delete=models.CASCADE, blank=True, null=True)
    name = models.TextField()
    url = models.TextField()
    snippet = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

# TODO: 
class UserCourseOutlineConversation(ChatConversation):
    course_parent_object = models.ForeignKey(UserCourse, on_delete=models.CASCADE, blank=True, null=True)

class UserCourseModuleNote(models.Model):
    course_module_object = models.ForeignKey(UserCourseModules, on_delete=models.CASCADE, blank=True, null=True)
    notes_md = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

class UserCourseModuleConversation(ChatConversation):
    course_module_object = models.ForeignKey(UserCourseModules, on_delete=models.CASCADE, blank=True, null=True)

class UserCourseModuleNoteQuestion(models.Model):
    course_note_object = models.ForeignKey(UserCourseModuleNote, on_delete=models.CASCADE, blank=True, null=True)
    question_number = models.IntegerField()
    question = models.TextField()
    multiple_choice_options = models.TextField(blank=True, null=True)
    answer = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)






# # class UserCourse(models.Model):
# #     initial_background_object = models.ForeignKey(UserBackgroundParent, on_delete=models.CASCADE, blank=True, null=True)
# #     name = models.CharField(max_length=3000)
# #     description = models.TextField()
# #     module_list = models.TextField()
# #     # outline = models.TextField()
# #     created_at = models.DateTimeField(auto_now_add=True)
# #     updated_at = models.DateTimeField(auto_now=True)

# # class UserCourseModules(models.Model):
# #     parent_course_object = models.ForeignKey(UserCourse, on_delete=models.CASCADE, blank=True, null=True)
# #     module_number = models.IntegerField(blank=True, null=True)
# #     module_topic = models.TextField()
# #     module_description = models.TextField()
# #     created_at = models.DateTimeField(auto_now_add=True)

# # class UserCourseModulesBingResult(models.Model):
# #     parent_course_object = models.ForeignKey(UserCourse, on_delete=models.CASCADE, blank=True, null=True)
# #     name = models.TextField()
# #     url = models.TextField()
# #     snippet = models.TextField()
# #     created_at = models.DateTimeField(auto_now_add=True)

# # class UserCourseOutlineConversation(ChatConversation):
# #     course_parent_object = models.ForeignKey(UserCourse, on_delete=models.CASCADE, blank=True, null=True)

# # class UserCourseModuleNote(models.Model):
# #     course_module_object = models.ForeignKey(UserCourseModules, on_delete=models.CASCADE, blank=True, null=True)
# #     notes_md = models.TextField()
# #     created_at = models.DateTimeField(auto_now_add=True)

# # class UserCourseModuleConversation(ChatConversation):
# #     course_module_object = models.ForeignKey(UserCourseModules, on_delete=models.CASCADE, blank=True, null=True)

# # class UserCourseModuleNoteQuestion(models.Model):
# #     course_note_object = models.ForeignKey(UserCourseModuleNote, on_delete=models.CASCADE, blank=True, null=True)
# #     question_number = models.IntegerField()
# #     question = models.TextField()
# #     multiple_choice_options = models.TextField(blank=True, null=True)
# #     answer = models.TextField()
# #     created_at = models.DateTimeField(auto_now_add=True)

