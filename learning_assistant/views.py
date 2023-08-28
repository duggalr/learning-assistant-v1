from django.shortcuts import render



# TODO: 
    # build actual site/functionality first 
    # add user and all the other stuff after


def home(request):
    return render(request, 'home.html')


