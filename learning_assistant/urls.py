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
    path("playground", views.playground, name="playground"),
    path("handle_user_message", views.handle_user_message, name="handle_user_message"),
    path("save_user_code", views.save_user_code, name="save_user_code"),

    path("handle_file_name_change", views.handle_file_name_change, name="handle_file_name_change"),

]

