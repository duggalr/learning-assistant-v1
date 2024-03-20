from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.http import JsonResponse

import os


if 'PRODUCTION' not in os.environ:
    from dotenv import load_dotenv, find_dotenv
    dot_env_file = find_dotenv()
    load_dotenv(dot_env_file)


def landing(request):
    return render(request, 'landing.html')


def playground(request):
    return render(request, 'playground.html')


