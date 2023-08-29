from django.shortcuts import render
from django.http import JsonResponse

from . import main_utils



# TODO: 
    # build actual site/functionality first 
    # add user and all the other stuff after


def home(request):
    return render(request, 'home.html')


def handle_user_message(request):

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

        return JsonResponse({'success': True, 'response': model_response_dict})


