from django.shortcuts import render, redirect, get_object_or_404

from .models import *

# from acc.models import CustomUser, AnonUser
from .scripts import utils


def landing(request):
    custom_user_obj = utils._get_customer_user(request)
    anon_user = utils._check_if_anon_user(custom_user_obj)

    return render(request, 'landing.html',  {
        'anon_user': anon_user
    })


def about(request):
    custom_user_obj = utils._get_customer_user(request)
    anon_user = utils._check_if_anon_user(custom_user_obj)

    return render(request, 'about.html', {
        'anon_user': anon_user
    })


def playground(request):
    custom_user_obj = utils._get_customer_user(request)
    anon_user = utils._check_if_anon_user(custom_user_obj)

    code_id = request.GET.get('cid', None)

    uc_obj = None
    user_conversation_objects = []
    if code_id is not None and not anon_user:
        uc_obj = get_object_or_404(PlaygroundCode, id = code_id)
        user_conversation_objects = PlaygroundConversation.objects.filter(
            code_obj = uc_obj
        ).order_by('created_at')

    current_user_email = None
    if custom_user_obj.oauth_user is not None:
        current_user_email = custom_user_obj.oauth_user.email

    return render(request, 'playground.html', {    
        'anon_user': anon_user,
        'customer_user_obj': custom_user_obj,
        'current_user_email': current_user_email,
        'code_id': code_id,
        'uc_obj': uc_obj,
        'user_conversation_objects': user_conversation_objects,
    })


  

