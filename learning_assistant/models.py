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


class LandingEmailSubscription(models.Model):
    email = models.EmailField()
    created_at = models.DateTimeField(auto_now_add=True)



# TODO: 
    # save a question with the test-case
    # from there, create the student and teacher view / logic on how each will see the questions
        # from there, implement the student functionality to interact with the video + submit questions (test-case, etc)
            # add all the q-completed logic <-- very similar to coding-bat





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


