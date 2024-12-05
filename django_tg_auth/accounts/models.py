# accounts/models.py
# Django приложение: accounts

from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    telegram_id = models.BigIntegerField(null=True, blank=True, unique=True)
    telegram_username = models.CharField(max_length=150, null=True, blank=True)

    def __str__(self):
        return self.username or f"Telegram User {self.telegram_id}"
