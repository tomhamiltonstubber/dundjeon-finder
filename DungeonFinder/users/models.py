from datetime import datetime, timezone

from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models
from django.db.models import QuerySet
from django.urls import reverse

from DungeonFinder.storage import PublicStorage


class UserManager(BaseUserManager):
    def _create_user(self, email, password, is_admin=False, **extra_fields):
        """Create and save a User with the given email and password."""
        email = self.normalize_email(email)
        user = self.model(email=email, is_admin=is_admin, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_user(self, email, password=None, **extra_fields):
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        return self._create_user(email, password, is_admin=True, **extra_fields)


class User(AbstractUser):
    objects = UserManager.from_queryset(QuerySet)()

    email = models.EmailField('Email Address', unique=True)
    first_name = models.CharField('First name', max_length=30, blank=True)
    last_name = models.CharField('Last name', max_length=150, blank=True)
    last_logged_in = models.DateTimeField(
        'Last Logged in', default=datetime(2020, 1, 1, tzinfo=timezone.utc), editable=False
    )
    avatar = models.ImageField('Avatar', upload_to='avatars', blank=True, null=True)
    screen_name = models.CharField(
        max_length=150,
        unique=True,
        help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.',
        validators=[UnicodeUsernameValidator],
        error_messages={'unique': 'A user with that screen name already exists.'},
    )
    is_active = models.BooleanField(
        default=True, help_text='Unselect this instead of deleting accounts.', editable=False
    )
    is_admin = models.BooleanField('Is super user', default=False, editable=False)

    # We aren't using username as the unique field here. Instead, people can enter a screen name.
    username = None
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return f'{self.screen_name}'

    def get_absolute_url(self):
        return reverse('profile')

    @property
    def is_gm(self):
        return hasattr(self, 'gamemaster')

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'


class GameMaster(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='gamemaster')

    def __str__(self):
        if self.user.screen_name:
            return self.user.screen_name
        return f'{self.user.first_name} {self.user.last_name[0]}'
