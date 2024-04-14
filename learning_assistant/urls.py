from django.urls import path

from . import views


urlpatterns = [

    ## Generic Views
    path("", views.landing, name="landing"),
    path("about", views.about, name="about"),

    ## Playground
    path("playground", views.playground, name="playground"),
    path("handle_playground_user_message", views.handle_playground_user_message, name="handle_playground_user_message"),
    path("save_user_code", views.save_user_playground_code, name="save_user_code"),
    # path("handle_file_name_change", views.handle_file_name_change, name="handle_file_name_change"),
    
    ## General CS Tutor
    path("general_cs_tutor", views.general_cs_tutor, name="general_cs_tutor"),
    
    # ## Course Gen
    # path("course-gen/background-chat", views.course_generation_background_chat, name="course_gen_bg_chat"),
]
