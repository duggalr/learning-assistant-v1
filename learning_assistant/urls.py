from django.urls import path

from . import views


urlpatterns = [

    # Auth0
    path("login", views.login, name="login"),
    path("logout", views.logout, name="logout"),
    path("callback", views.callback, name="callback"),

    # Primary Views
    path("", views.landing, name="landing"),
    path("about", views.about, name="about"),
    path("dashboard", views.dashboard, name="dashboard"),
    
    path("practice-questions", views.practice_questions, name="practice_questions"),

    path("general-tutor", views.general_cs_tutor, name="general_cs_tutor"),
    path("handle_general_tutor_user_message", views.handle_general_tutor_user_message, name="handle_general_tutor_user_message"),

    # path("lesson-plan", views.lesson_dashboard, name="lesson_dashboard"),
    # path("questions/<int:lid>", views.questions, name="questions"),

    path("playground", views.playground, name="playground"),
    path("handle_user_message", views.handle_user_message, name="handle_user_message"),
    path("save_user_code", views.save_user_code, name="save_user_code"),

    path("handle_file_name_change", views.handle_file_name_change, name="handle_file_name_change"),

    # path("handle_code_submit", views.handle_code_submit, name="handle_code_submit"),

    # # Admin Views
    path("admin-dashboard", views.super_user_admin_dashboard, name="super_user_admin_dashboard"),
    path("admin-student-profile/<int:uid>", views.super_user_admin_student_page, name="super_user_admin_student_page"),
    
    # Teacher-Student Views
    path("teacher-admin/signup", views.teacher_admin_signup, name="teacher_admin_signup"),
    path("teacher-admin/login", views.teacher_admin_login, name="teacher_admin_login"),

    path("teacher-admin/dashboard", views.teacher_admin_dashboard, name="teacher_admin_dashboard"),    
    path("teacher-admin/manage/students", views.teacher_admin_student_management, name="teacher_admin_student_management"),
    path("teacher-admin/manage/questions", views.teacher_admin_question_management, name="teacher_admin_question_management"),
    path("teacher-admin/assistant", views.teacher_admin_assistant_chat, name="teacher_admin_assistant_chat"),

    path("student-admin/create/account", views.student_admin_account_create, name="student_admin_account_create"),
    path("student-admin/account/login", views.student_admin_login, name="student_admin_login"),
    path("student-admin/dashboard", views.student_admin_dashboard, name="student_admin_dashboard"),
    path("student-admin/playground", views.student_admin_playground, name="student_admin_playground"),

    path("student-admin/handle-tutor-message", views.student_tutor_handle_message, name="student_tutor_handle_message"),
    path("teacher-admin/handle-tutor-message", views.teacher_assistant_handle_message, name="teacher_assistant_handle_message"),

    path("student-admin/handle-playground-message", views.handle_student_playground_message, name="handle_student_playground_message"),
    path("student-admin/save-playground-code", views.save_student_playground_code, name="save_student_playground_code"),


    path("teacher-admin/student-profile/<int:uid>", views.teacher_admin_student_view, name="teacher_admin_student_view"),

    path("teacher-admin/question/delete", views.teacher_question_delete, name="teacher_question_delete"),
    path("teacher-admin/student/delete", views.teacher_student_delete, name="teacher_student_delete"),


    path("teacher-admin/question/<int:qid>", views.teacher_specific_question_view, name="teacher_specific_question_view"),

    
    path("landing_teacher_email_input", views.landing_teacher_email_input, name="landing_teacher_email_input"),

    ## Files
    path("handle_user_file_upload", views.handle_user_file_upload, name="handle_user_file_upload"),
    path("file_view/<int:file_id>", views.user_file_viewer, name="user_file_view"),
    path("handle_user_file_question", views.handle_user_file_question, name="handle_user_file_question"),

    # # General New Views
    # path("new_landing", views.new_landing_main, name="new_landing_main"),

]

