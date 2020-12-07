from datetime import datetime, timezone

from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.db import models


class UserManager(BaseUserManager):
    def _create_user(self, email, company, password, is_superuser=False, **extra_fields):
        """Create and save a User with the given email and password."""
        email = self.normalize_email(email)
        user = self.model(email=email, is_superuser=is_superuser, company=company, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_user(self, email, company, password=None, **extra_fields):
        return self._create_user(email, company, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        return super().create_superuser(email, password, is_superuser=True, **extra_fields)


class User(AbstractUser):
    username = models.CharField('Username', unique=True)
    email = models.EmailField('Email Address', unique=True)
    first_name = models.CharField('First name', max_length=30, blank=True)
    last_name = models.CharField('Last name', max_length=150, blank=True)
    last_logged_in = models.DateTimeField('Last Logged in', default=datetime(2020, 1, 1, tzinfo=timezone.utc))

    def __str__(self):
        return f'{self.username}'

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'


class GameMaster(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
