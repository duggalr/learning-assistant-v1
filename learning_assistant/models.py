from django.db import models

# Create your models here.


class UserOAuth(models.Model):
    auth_type = models.CharField(max_length=500)
    email = models.EmailField()
    email_verified = models.BooleanField()
    name = models.TextField()
    created_at = models.IntegerField()
    updated_at = models.IntegerField()


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


class UserCode(models.Model):
    user_auth_obj = models.ForeignKey(UserOAuth, on_delete=models.CASCADE, blank=True, null=True)
    lesson_question_obj = models.ForeignKey(LessonQuestion, on_delete=models.CASCADE, blank=True, null=True)
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


class LessonQuestionTestCase(models.Model):
    lesson_question_obj = models.ForeignKey(LessonQuestion, on_delete=models.CASCADE)
    input_param = models.CharField(max_length=5000, blank=True, null=True)
    correct_output = models.CharField(max_length=5000, blank=True, null=True)
    test_case_full_text = models.TextField(blank=True, null=True)


# class UserGeneralTutorParent(models.Model):
#     user_auth_obj = models.ForeignKey(UserOAuth, on_delete=models.CASCADE, blank=True, null=True)
#     created_at = models.DateTimeField(auto_now_add=True)


class UserGeneralTutorConversation(models.Model):
    user_auth_obj = models.ForeignKey(UserOAuth, on_delete=models.CASCADE, blank=True, null=True)
    # gt_parent_obj = models.ForeignKey(UserGeneralTutorParent, on_delete=models.CASCADE)
    question = models.CharField(max_length=3000)
    question_prompt = models.TextField()
    response = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)


# TODO:
    # need to add school
    # custom user model as abstract base class for teacher student would be ideal

## Teacher-Student Models
class Teacher(models.Model):
    full_name = models.CharField(max_length=1000)
    email = models.EmailField(max_length=500)
    password = models.CharField(max_length=1000)
    created_at = models.DateTimeField(auto_now_add=True)


class TeacherStudentInvite(models.Model):
    student_email = models.EmailField(max_length=500)
    teacher_obj = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)


class Student(models.Model):
    full_name = models.CharField(max_length=1000)
    email = models.EmailField(max_length=500)
    password = models.CharField(max_length=1000)
    teacher_obj = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)







# class NewPracticeQuestion(models.Model):
#     question_name = models.CharField(max_length=3000)
#     question_text = models.TextField()
#     created_at = models.DateTimeField(auto_now_add=True)


# class NewPracticeTestCase(models.Model):
#     question_obj = models.ForeignKey(NewPracticeQuestion, on_delete=models.CASCADE)
#     test_case_text = models.TextField()
#     created_at = models.DateTimeField(auto_now_add=True)
#     # input_param = models.CharField(max_length=5000)
#     # correct_output = models.CharField(max_length=5000)



# class LessonQuestionStatus(models.Model):
#     lesson_question_obj = models.ForeignKey(LessonQuestion, on_delete=models.CASCADE, blank=True, null=True)
#     status = models.CharField(max_length=3000)
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)

