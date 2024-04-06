from django.db import models
from django.utils import timezone


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
    unique_anon_user_id = models.CharField(max_length=100, blank=True, null=True)
    code_unique_name = models.CharField(max_length=2000)
    user_code = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class UserConversation(models.Model):
    user_auth_obj = models.ForeignKey(UserOAuth, on_delete=models.CASCADE, blank=True, null=True)
    code_obj = models.ForeignKey(UserCode, on_delete=models.CASCADE)
    unique_anon_user_id = models.CharField(max_length=100, blank=True, null=True)
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

# will be one to many --> all gt-conv will link to this (even for case of anon)
class UserGeneralTutorParent(models.Model):
    user_auth_obj = models.ForeignKey(UserOAuth, on_delete=models.CASCADE, blank=True, null=True)
    unique_anon_user_id = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

class UserGeneralTutorConversation(models.Model):
    user_auth_obj = models.ForeignKey(UserOAuth, on_delete=models.CASCADE, blank=True, null=True)
    # gt_parent_obj = models.ForeignKey(UserGeneralTutorParent, on_delete=models.CASCADE)

    chat_parent_object = models.ForeignKey(UserGeneralTutorParent, on_delete=models.CASCADE, blank=True, null=True)
    unique_anon_user_id = models.CharField(max_length=100, blank=True, null=True)
    question = models.CharField(max_length=3000)
    question_prompt = models.TextField()
    response = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)




## Personal Course Gen Models
class ChatParent(models.Model):
    user_auth_obj = models.ForeignKey(UserOAuth, on_delete=models.CASCADE, blank=True, null=True)
    unique_anon_user_id = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class ChatConversation(models.Model):
    user_auth_obj = models.ForeignKey(UserOAuth, on_delete=models.CASCADE, blank=True, null=True)
    unique_anon_user_id = models.CharField(max_length=100, blank=True, null=True)
    question = models.CharField(max_length=3000)
    question_prompt = models.TextField()
    response = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

class UserBackgroundParent(ChatParent):
    final_response = models.TextField(blank=True, null=True)

class UserBackgroundConversation(ChatConversation):
    chat_parent_object = models.ForeignKey(UserBackgroundParent, on_delete=models.CASCADE, blank=True, null=True)

class UserCourse(models.Model):
    initial_background_object = models.ForeignKey(UserBackgroundParent, on_delete=models.CASCADE, blank=True, null=True)
    name = models.CharField(max_length=3000)
    description = models.TextField()
    outline = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

class UserCourseOutlineConversation(ChatConversation):
    course_parent_object = models.ForeignKey(UserCourse, on_delete=models.CASCADE, blank=True, null=True)

# TODO: given this model format, add in code and go from there




## Teacher-Student Models
class Teacher(models.Model):
    full_name = models.CharField(max_length=1000)
    email = models.EmailField(max_length=500)
    password = models.CharField(max_length=1000)
    created_at = models.DateTimeField(auto_now_add=True)


class TeacherStudentInvite(models.Model):
    student_email = models.EmailField(max_length=500)
    teacher_obj = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    student_registered = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(default=timezone.now)


class Student(models.Model):
    full_name = models.CharField(max_length=1000)
    email = models.EmailField(max_length=500)
    password = models.CharField(max_length=1000)
    teacher_obj = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    

class TeacherQuestion(models.Model):
    question_name = models.TextField()
    question_text = models.TextField()
    teacher_obj = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)


class TeacherQuestionTestCase(models.Model):
    teacher_question_obj = models.ForeignKey(TeacherQuestion, on_delete=models.CASCADE)
    input_param = models.CharField(max_length=5000, blank=True, null=True)
    correct_output = models.CharField(max_length=5000, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)


class StudentConversation(models.Model):
    student_obj = models.ForeignKey(Student, on_delete=models.CASCADE)
    question = models.CharField(max_length=3000)
    question_prompt = models.TextField()
    response = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

# TODO:
class TeacherConversation(models.Model):
    teacher_obj = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    question = models.CharField(max_length=3000)
    question_prompt = models.TextField()
    response = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)


class StudentPlaygroundCode(models.Model):
    student_obj = models.ForeignKey(Student, on_delete=models.CASCADE)
    teacher_question_obj = models.ForeignKey(TeacherQuestion, on_delete=models.CASCADE)
    user_code = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)


class StudentPlaygroundConversation(models.Model):
    student_obj = models.ForeignKey(Student, on_delete=models.CASCADE)
    code_obj = models.ForeignKey(StudentPlaygroundCode, on_delete=models.CASCADE)
    question = models.CharField(max_length=3000)
    question_prompt = models.TextField()
    response = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)


# TODO:
class UserFiles(models.Model):
    user_auth_obj = models.ForeignKey(UserOAuth, on_delete=models.CASCADE, blank=True, null=True)
    file_name = models.CharField(max_length=2000)
    file_path = models.FileField(upload_to='documents/')
    uploaded_at = models.DateTimeField(auto_now_add=True)


class FilePineCone(models.Model):
    user_auth_obj = models.ForeignKey(UserOAuth, on_delete=models.CASCADE, blank=True, null=True)
    file_obj = models.ForeignKey(UserFiles, on_delete=models.CASCADE)
    file_namespace = models.CharField(max_length=3000)


class UserFileConversation(models.Model):
    user_auth_obj = models.ForeignKey(UserOAuth, on_delete=models.CASCADE, blank=True, null=True)
    file_obj = models.ForeignKey(UserFiles, on_delete=models.CASCADE)
    question = models.CharField(max_length=3000)
    question_prompt = models.TextField()
    retrieved_numbers_list = models.CharField(max_length=3000, blank=True, null=True)
    response = models.TextField()
    response_with_citations = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)


class LandingTeacherEmail(models.Model):
    email = models.EmailField()
    created_at = models.DateTimeField(auto_now_add=True)



## New Course Modals ## 

class PythonCourseLesson(models.Model):
    lesson_title = models.CharField(max_length=3000)
    lesson_description = models.TextField()
    lesson_video = models.URLField()
    order_number = models.IntegerField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)


class PythonLessonQuestion(models.Model):
    question_name = models.CharField(max_length=3000)
    question_text = models.TextField()
    course_lesson_obj = models.ForeignKey(PythonCourseLesson, on_delete=models.CASCADE)
    order_number = models.IntegerField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)


class PythonLessonQuestionTestCase(models.Model):
    lesson_question_obj = models.ForeignKey(PythonLessonQuestion, on_delete=models.CASCADE)
    input_param = models.CharField(max_length=5000, blank=True, null=True)
    correct_output = models.CharField(max_length=5000, blank=True, null=True)


class PythonLessonUserCode(models.Model):
    user_auth_obj = models.ForeignKey(UserOAuth, on_delete=models.CASCADE, blank=True, null=True)
    lesson_question_obj = models.ForeignKey(PythonLessonQuestion, on_delete=models.CASCADE, blank=True, null=True)
    code_unique_name = models.CharField(max_length=2000)
    user_code = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)


class PythonLessonConversation(models.Model):
    user_auth_obj = models.ForeignKey(UserOAuth, on_delete=models.CASCADE, blank=True, null=True)
    code_obj = models.ForeignKey(PythonLessonUserCode, on_delete=models.CASCADE)
    question = models.CharField(max_length=3000)
    question_prompt = models.TextField()
    response = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)


class PythonLessonQuestionUserSubmission(models.Model):  # keeps track of all user submissions
    user_auth_obj = models.ForeignKey(UserOAuth, on_delete=models.CASCADE, blank=True, null=True)
    lesson_question_obj = models.ForeignKey(PythonLessonQuestion, on_delete=models.CASCADE, blank=True, null=True)
    code_str = models.TextField()
    complete = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)    


class LandingEmailSubscription(models.Model):
    email = models.EmailField()
    created_at = models.DateTimeField(auto_now_add=True)


class PythonLessonVideoConversation(models.Model):
    user_auth_obj = models.ForeignKey(UserOAuth, on_delete=models.CASCADE, blank=True, null=True)
    course_lesson_obj = models.ForeignKey(PythonCourseLesson, on_delete=models.CASCADE)
    question = models.CharField(max_length=3000)
    response = models.TextField()
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


