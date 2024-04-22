import uuid
from django.db import models


class AnonUser(models.Model):
    """
    Created for all visitors on site.
        - Allows us to track user activity (since functionality on site is accessible without login), conversion rates, etc. 
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

class UserOAuth(models.Model):
    """
    User has signed up using Auth0.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    auth_type = models.CharField(max_length=500)
    email = models.EmailField()
    email_verified = models.BooleanField()
    name = models.TextField()

class CustomUser(models.Model):
    """
    Abstract class used downstream.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    anon_user = models.OneToOneField(AnonUser, on_delete=models.CASCADE, null=True, blank=True)
    oauth_user = models.OneToOneField(UserOAuth, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
