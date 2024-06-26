from django.urls import path
from . import views


urlpatterns = [

    ## Generic Views
    path("", views.landing, name="landing"),
    # path("about", views.about, name="about"),
    path("blog", views.blog, name="blog"),
    path("blog/v1-release", views.blog_v1_release, name="blog_v1_release"),
    path("faq", views.faq, name="faq"),

    ## Playground
    path("playground/ide", views.playground, name="playground"),
    path("playground/handle_user_message", views.handle_playground_user_message, name="handle_playground_user_message"),
    path("playground/save_user_code", views.save_user_playground_code, name="save_user_playground_code"),
    path("handle_file_name_change", views.handle_playground_file_name_change, name="handle_file_name_change"),
    
    ## General CS Tutor
    path("chat/tutor", views.general_cs_tutor, name="general_cs_tutor"),
    path("chat/handle_user_message", views.handle_general_tutor_user_message, name="handle_general_tutor_user_message"),

    ## Authenticated User Dashboard
    path("dashboard", views.user_dashboard, name="dashboard"),

]
