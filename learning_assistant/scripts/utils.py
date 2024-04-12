import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "my_project.settings")
import django
django.setup()

import secrets
import string

# from learning_assistant.models import 
from acc.models import CustomUser, AnonUser


def _create_anon_custom_user():
    au_obj = AnonUser.objects.create()
    au_obj.save()

    cu_obj = CustomUser.objects.create(
        anon_user = au_obj
    )
    cu_obj.save()
    return cu_obj

def _get_customer_user(request):
    custom_user_id = request.session.get('custom_user_uuid', None)
    custom_user_obj = None
    if custom_user_id is None:
        custom_user_obj = _create_anon_custom_user()
        request.session['custom_user_uuid'] = custom_user_obj.id
    else:
        custom_user_obj = CustomUser.objects.get(id = custom_user_id)
    
    return custom_user_obj

def _check_if_anon_user(user_obj):
    anon_user = True
    if user_obj.oauth_user is not None:
        anon_user = False
    return anon_user

def _generate_random_string(k = 10):
    return ''.join([secrets.choice(string.ascii_lowercase) for idx in range(k)])
