from django.urls import path

from . import views


urlpatterns = [
    path("", views.home, name="home"),
    path("handle_user_message", views.handle_user_message, name="handle_user_message"),
]

