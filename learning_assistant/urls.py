from django.urls import path

from . import views


urlpatterns = [

    ## Generic Views
    path("", views.landing, name="landing"),
    path("about", views.about, name="about"),

    ## Playground
    path("playground", views.playground, name="playground"),
    path("handle_playground_user_message", views.handle_playground_user_message, name="handle_playground_user_message"),
    path("save_user_playground_code", views.save_user_playground_code, name="save_user_playground_code"),
    # path("handle_file_name_change", views.handle_file_name_change, name="handle_file_name_change"),
    
    ## General CS Tutor
    path("chat/tutor", views.general_cs_tutor, name="general_cs_tutor"),
    path("chat/handle_user_message", views.handle_general_tutor_user_message, name="handle_general_tutor_user_message"),
    
    # ## Course Gen
    # path("course-gen/background-chat", views.course_generation_background_chat, name="course_gen_bg_chat"),
    # path("course-gen/handle-background-message", views.handle_course_generation_background_message, name="handle_course_generation_background_message"),
    # path("course-gen/course-outline/<int:cid>", views.student_course_outline, name="student_course_outline"),
    # path("course-gen/course-home/<int:cid>", views.student_course_homepage, name="student_course_homepage"),
    # path("course-gen/list", views.all_student_courses, name="all_student_courses"),
    # path("course-gen/generate-module-notes", views.generate_module_notes, name="generate_module_notes"),
    # path("course-gen/notes/<int:mid>", views.course_module_notes_view, name="course_module_notes_view"),
    
]
