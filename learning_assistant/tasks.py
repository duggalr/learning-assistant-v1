from time import sleep
from django.core.mail import send_mail
from django.conf import settings
from celery import shared_task



@shared_task()
def send_student_account_create_email(message, user_email):    
    send_mail(
        subject="You have been invited to use Code Companion",
        message=message,
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[user_email],
        fail_silently=False
    )
    print('sent email!')

