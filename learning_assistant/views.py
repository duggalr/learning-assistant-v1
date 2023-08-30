from django.shortcuts import render, redirect
from django.urls import reverse
from django.http import JsonResponse
from urllib.parse import quote_plus, urlencode

import os
import time
from dotenv import load_dotenv, find_dotenv
from authlib.integrations.django_client import OAuth

from .models import *
from . import main_utils




if 'PRODUCTION' not in os.environ:
    dot_env_file = find_dotenv()
    load_dotenv(dot_env_file)


oauth = OAuth()
oauth.register(
    "auth0",
    client_id = os.environ['AUTH0_CLIENT_ID'],
    client_secret = os.environ['AUTH0_CLIENT_SECRET'],
    client_kwargs={
        "scope": "openid profile email",
    },
    server_metadata_url=f"https://{os.environ['AUTH0_DOMAIN']}/.well-known/openid-configuration",
)


## Auth0 Authentication Functions ##

def callback(request):
    token = oauth.auth0.authorize_access_token(request)
    request.session["user"] = token
    
    print(f"User Details: {token}")

    user_info = token['userinfo']
    user_email = user_info['email']
    user_auth_type = user_info['sub']
    user_email_verified = user_info['email_verified']
    user_name = user_info['name']
    updated_date_ts = user_info['iat']

    user_auth_objects = UserOAuth.objects.filter(email = user_email)
    if len(user_auth_objects) > 0:
        user_auth_obj = user_auth_objects[0]
        user_auth_obj.email_verified = user_email_verified
        user_auth_obj.auth_type = user_auth_type
        user_auth_obj.name = user_name
        user_auth_obj.updated_at = updated_date_ts
        user_auth_obj.save()
    else:
        current_unix_ts = int(time.time())
        user_auth_obj = UserOAuth.objects.create(
            auth_type = user_auth_type,
            email = user_email,
            email_verified = user_email_verified,
            name = user_name,
            created_at = current_unix_ts,
            updated_at = updated_date_ts
        )
        user_auth_obj.save()

    return redirect(request.build_absolute_uri(reverse("home")))


def login(request):
    return oauth.auth0.authorize_redirect(
        request, request.build_absolute_uri(reverse("callback"))
    )


def logout(request):
    request.session.clear()

    return redirect(
        f"https://{os.environ['AUTH0_DOMAIN']}/v2/logout?"
        + urlencode(
            {
                "returnTo": request.build_absolute_uri(reverse("landing")),
                "client_id": os.environ['AUTH0_CLIENT_ID'],
            },
            quote_via=quote_plus,
        ),
    )





## Primary View Functions ##

def landing(request):
    return render(request, 'landing.html')


def dashboard(request):
    initial_user_session = request.session.get("user")
    return render(request, 'dashboard.html',  {
        'user_session': initial_user_session
    })


def about(request):
    return render(request, 'about.html')


def handle_user_message(request):

    # initial_user_session = request.session.get("user")

    if request.method == 'POST':

        print('form-data:', request.POST)

        user_question = request.POST['message'].strip()
        user_code = request.POST['user_code'].strip()

        print('code:', user_code)

        model_response_dict = main_utils.main_handle_question(
            question = user_question,
            student_code = user_code
        )
        print('model-response:', model_response_dict)

        user_oauth_obj = None
        # if initial_user_session is not None:
        #     user_oauth_obj = UserOAuth.objects.get(email = initial_user_session['userinfo']['email'])

        ur_obj = UserResponse.objects.create(
            user_auth_obj = user_oauth_obj,
            question = model_response_dict['question'],
            question_prompt = model_response_dict['q_prompt'],
            response = model_response_dict['response'],
        )
        ur_obj.save()

        return JsonResponse({'success': True, 'response': model_response_dict})


