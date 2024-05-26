from django.contrib.auth.models import AbstractUser
from django.db import models
import uuid

class CustomUser(AbstractUser):
    # Add any additional fields you need for your user model
    contact = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.username

class ApiKey(models.Model):
    key = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='api_keys')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.key)