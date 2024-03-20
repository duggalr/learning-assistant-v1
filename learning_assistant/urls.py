from django.urls import path

from . import views


urlpatterns = [
    path("", views.landing, name="landing"),
    path("playground", views.playground, name="playground"),
]
