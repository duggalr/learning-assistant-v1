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
    
    path("lesson-plan", views.lesson_dashboard, name="lesson_dashboard"),
    path("questions/<int:lid>", views.questions, name="questions"),


    path("playground", views.playground, name="playground"),
    path("handle_user_message", views.handle_user_message, name="handle_user_message"),
    path("save_user_code", views.save_user_code, name="save_user_code"),

    path("handle_file_name_change", views.handle_file_name_change, name="handle_file_name_change"),

    # path("handle_code_submit", views.handle_code_submit, name="handle_code_submit"),

    # Admin Views
    path("admin-dashboard", views.teacher_admin_dashboard, name="teacher_admin_dashboard"),
    path("admin-student-profile/<int:uid>", views.teacher_admin_student_page, name="teacher_admin_student_page"),

]

