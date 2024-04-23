from django.urls import path

from . import views


urlpatterns = [

    ## Primary Views
    path("", old_views_two.landing, name="landing"),
    path("about", old_views_two.about, name="about"),

    ## Playground
    path("playground", old_views_two.playground, name="playground"),
    path("handle_user_message", old_views_two.handle_user_message, name="handle_user_message"),
    path("save_user_code", old_views_two.save_user_code, name="save_user_code"),
    path("handle_file_name_change", old_views_two.handle_file_name_change, name="handle_file_name_change"),


    # path("dashboard", old_views_two.dashboard, name="dashboard"),
    path("cs-tutor", old_views_two.general_cs_tutor, name="general_cs_tutor"),
    path("handle_general_tutor_user_message", old_views_two.handle_general_tutor_user_message, name="handle_general_tutor_user_message"),

    ## Personal Course Gen Stuff
    path("all_student_courses", old_views_two.all_student_courses, name="all_student_courses"),
    path("course-gen/background", old_views_two.course_generation_student_background_chat, name="course_generation_student_background_chat"),

    path("handle_student_background_chat_message", old_views_two.handle_student_background_chat_message, name="handle_student_background_chat_message"),
    path("student_course_outline", old_views_two.student_course_outline, name="student_course_outline"),
    path("student_course_outline_handle_message", old_views_two.student_course_outline_handle_message, name="student_course_outline_handle_message"),
    path("personal_course_homepage/<int:cid>", old_views_two.personal_course_homepage, name="personal_course_homepage"),
    path("generate_module_notes", old_views_two.generate_module_notes, name="generate_module_notes"),
    path("course_module_notes_view/<int:mid>", old_views_two.course_module_notes_view, name="course_module_notes_view"),






    # ## Admin Views
    # path("admin-dashboard", views.super_user_admin_dashboard, name="super_user_admin_dashboard"),
    # path("admin-student-profile/<int:uid>", views.super_user_admin_student_page, name="super_user_admin_student_page"),


    ## Custom Learning Views
    # path("super_user_motivation_prompt", views.super_user_motivation_prompt, name="super_user_motivation_prompt"),

    # ## New Python Course Home
    # path("python-course", views.new_course_home, name="new_course_home"),
    # path("python-lesson/<int:lid>", views.new_course_lesson_page, name="new_course_lesson_page"),
    
    # path("python-playground", views.new_course_playground, name="new_course_playground"),
    # path("new_course_handle_user_message", views.new_course_handle_user_message, name="new_course_handle_user_message"),
    # path("new_course_handle_solution_submit", views.new_course_handle_solution_submit, name="new_course_handle_solution_submit"),
    # path("new_course_save_user_code", views.new_course_save_user_code, name="new_course_save_user_code"),
    # path("new_course_video_handle_message", views.new_course_video_handle_message, name="new_course_video_handle_message"),
    # path("new_course_random_question", views.new_course_random_question, name="new_course_random_question"),
    # path("admin-python-lesson", views.admin_new_course_dashboard, name="admin_new_course_dashboard"),
    # path("admin-python-lesson-management", views.admin_new_course_lesson_management, name="admin_new_course_lesson_management"),
    # path("admin-python-lesson-question-management/<int:lid>", views.admin_new_course_lesson_question_management, name="admin_new_course_lesson_question_management"),
    # path("admin-python-question-view/<int:qid>", views.admin_new_course_question_view, name="admin_new_course_question_view"),
    # path("admin-python-lesson-order-management", views.admin_new_course_lesson_order_management, name="admin_new_course_lesson_order_management"),
    # path("admin-python-lesson-delete", views.admin_new_course_lesson_delete, name="admin_new_course_lesson_delete"),
    # path("admin-python-question_delete", views.admin_new_course_question_delete, name="admin_new_course_question_delete"),
    # path("admin-python-question-order-management", views.admin_new_course_question_order_management, name="admin_new_course_question_order_management"),
    # path("admin-python-question-handle-feedback", views.new_course_handle_ai_feedback, name="new_course_handle_ai_feedback"),

]