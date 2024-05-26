from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    # Add any additional fields you need for your user model
    contact = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.username
