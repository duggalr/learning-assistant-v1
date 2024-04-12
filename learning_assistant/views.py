from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse

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
        'custom_user_obj': custom_user_obj,
        'custom_user_obj_id': custom_user_obj.id,
        'current_user_email': current_user_email,
        'code_id': code_id,
        'uc_obj': uc_obj,
        'user_conversation_objects': user_conversation_objects,
    })


def save_user_code(request):

    custom_user_obj = utils._get_customer_user(request)

    if request.method == 'POST':

        print('save-user-code-POST:', request.POST)

        cid = request.POST['cid']
        custom_user_obj_id = request.POST['custom_user_obj_id']
        user_code = request.POST['user_code'].strip()
        user_code = user_code.replace('`', '"').strip()
        
        custom_user_objects = CustomUser.objects.filter(id = custom_user_obj_id)        
        if len(custom_user_objects) == 0:
            return JsonResponse({'success': False, 'response': 'User not found.'})

        custom_user_obj = custom_user_objects[0]

        if cid == 'None':

            rnd_code_filename = utils._generate_random_string(k = 10)
            uc_obj = PlaygroundCode.objects.create(
                user_obj = custom_user_obj,
                code_unique_name = rnd_code_filename,
                user_code = user_code
            )
            uc_obj.save()

            return JsonResponse({'success': True, 'cid': uc_obj.id, 'code_file_name': uc_obj.code_unique_name})
    
        else:
            # uc_objects = UserCode.objects.filter(id = cid, user_auth_obj = user_auth_obj)

            uc_objects = PlaygroundCode.objects.filter(
                id = cid,
                user_obj = custom_user_obj
            )

            if len(uc_objects) == 0:
                return JsonResponse({'success': False, 'response': 'Object not found.'})
            
            uc_obj = uc_objects[0]
            uc_obj.user_code = user_code
            uc_obj.save()
            return JsonResponse({'success': True, 'cid': uc_obj.id})



def handle_file_name_change(request):

    custom_user_obj = utils._get_customer_user(request)

    if request.method == 'POST':
        
        cid = request.POST['cid']
        custom_user_obj_id = request.POST['custom_user_obj_id']
        new_file_name = request.POST['new_file_name'].strip()
        user_code = request.POST['user_code'].strip()
        user_code = user_code.replace('`', '"').strip()

        custom_user_objects = CustomUser.objects.filter(id = custom_user_obj_id)        
        if len(custom_user_objects) == 0:
            return JsonResponse({'success': False, 'response': 'User not found.'})

        custom_user_obj = custom_user_objects[0]

        if cid == 'None':
            uc_obj = PlaygroundCode.objects.create(
                user_obj = custom_user_obj,
                code_unique_name = new_file_name,
                user_code = user_code
            )
            uc_obj.save()

        else:
            uc_obj = PlaygroundCode.objects.get(
                id = cid,
                user_obj = custom_user_obj
            )
            uc_obj.code_unique_name = new_file_name
            uc_obj.save()

        return JsonResponse({'success': True, 'cid': uc_obj.id, 'new_file_name': new_file_name})



