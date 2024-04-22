"""
Leveraging Auth0 for managing user authentication
"""
from django.shortcuts import redirect
from django.urls import reverse
from django.conf import settings
import os
import time
from urllib.parse import quote_plus, urlencode
from authlib.integrations.django_client import OAuth

from .models import UserOAuth, CustomUser


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

### Auth0 Authentication Functions ###

def callback(request):

    token = oauth.auth0.authorize_access_token(request)
    request.session["user"] = token

    user_info = token['userinfo']
    user_email = user_info['email']
    user_auth_type = user_info['sub']
    user_email_verified = user_info['email_verified']
    user_name = user_info['name']

    custom_user_obj_id = request.session.get("custom_user_uuid", None)
    custom_user_obj = None
    if custom_user_obj_id is not None:
        custom_user_objects = CustomUser.objects.filter(id = custom_user_obj_id)
        if len(custom_user_objects) > 0:
            custom_user_obj = custom_user_objects[0]
    
    if custom_user_obj is not None and custom_user_obj.oauth_user is not None:
        user_auth_obj = UserOAuth.objects.get(email = user_email)
        user_auth_obj.email_verified = user_email_verified
        user_auth_obj.auth_type = user_auth_type
        user_auth_obj.name = user_name
        user_auth_obj.save()
    
    elif custom_user_obj is not None:
        user_auth_obj = UserOAuth.objects.create(
            auth_type = user_auth_type,
            email = user_email,
            email_verified = user_email_verified,
            name = user_name,
        )
        user_auth_obj.save()

        custom_user_obj.oauth_user = user_auth_obj
        custom_user_obj.save()
    
    else: # should be a very rare case since custom user will already be created when user visits site
        
        user_auth_obj = UserOAuth.objects.create(
            auth_type = user_auth_type,
            email = user_email,
            email_verified = user_email_verified,
            name = user_name,
        )
        user_auth_obj.save()

        custom_user_obj = CustomUser.objects.create(
            oauth_user = user_auth_obj
        )
        custom_user_obj.save()

    request.session['custom_user_uuid'] = str(custom_user_obj.id)
    return redirect(request.build_absolute_uri(reverse(settings.AUTH0_CALLBACK_SUCCESS_REDIRECT_VIEW)))


def login(request):
    return oauth.auth0.authorize_redirect(
        request, request.build_absolute_uri(reverse("callback"))
    )


def signup(request):
    return oauth.auth0.authorize_redirect(
        request, request.build_absolute_uri(reverse("callback"))
    )


def logout(request):
    request.session.clear()
    return redirect(
        f"https://{os.environ['AUTH0_DOMAIN']}/v2/logout?"
        + urlencode(
            {
                # "returnTo": request.build_absolute_uri(settings.AUTH0_LOGOUT_REDIRECT_VIEW),
                "returnTo": request.build_absolute_uri(reverse('landing')),
                "client_id": os.environ['AUTH0_CLIENT_ID'],
            },
            quote_via=quote_plus,
        ),
    )
