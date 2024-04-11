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

from .models import UserOAuth


# TODO:
    # start here by implementing this new acc-functionality in our app
        # go from there


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

    user_info = token['userinfo']
    user_email = user_info['email']
    user_auth_type = user_info['sub']
    user_email_verified = user_info['email_verified']
    user_name = user_info['name']
    # updated_date_ts = user_info['iat']

    user_auth_objects = UserOAuth.objects.filter(email = user_email)
    if len(user_auth_objects) > 0:
        user_auth_obj = user_auth_objects[0]
        user_auth_obj.email_verified = user_email_verified
        user_auth_obj.auth_type = user_auth_type
        user_auth_obj.name = user_name
        # user_auth_obj.updated_at = updated_date_ts
        user_auth_obj.save()
    else:
        # current_unix_ts = int(time.time())
        user_auth_obj = UserOAuth.objects.create(
            auth_type = user_auth_type,
            email = user_email,
            email_verified = user_email_verified,
            name = user_name,
            # created_at = current_unix_ts,
            # updated_at = updated_date_ts
        )
        user_auth_obj.save()

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
                "returnTo": request.build_absolute_uri(settings.AUTH0_LOGOUT_REDIRECT_VIEW),
                "client_id": os.environ['AUTH0_CLIENT_ID'],
            },
            quote_via=quote_plus,
        ),
    )


