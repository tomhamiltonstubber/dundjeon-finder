from datetime import datetime

from django.contrib import messages
from django.contrib.auth import login as dj_login, user_logged_in
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.hashers import make_password
from django.contrib.auth.views import LoginView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.cache import cache
from django.core.exceptions import PermissionDenied
from django.db import IntegrityError
from django.dispatch import receiver
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.generic import TemplateView
from pytz import utc

from DungeonFinder.common.views import DFFormView, generate_random_key
from DungeonFinder.users.forms import UserSignupForm
from DungeonFinder.users.forms import UserUpdateThemeForm
from DungeonFinder.users.models import User


class GMRequestMixin:
    def dispatch(self, request, *args, **kwargs):
        if not (request.user.is_authenticated and request.user.is_gm):
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)


class Login(LoginView):
    template_name = 'users/login.jinja'
    title = 'Login'
    form_class = AuthenticationForm
    redirect_authenticated_user = True

    def get_redirect_url(self):
        return reverse('dashboard')

    def get_context_data(self, **kwargs):
        return super().get_context_data(title=self.title, **kwargs)


login = Login.as_view()


@receiver(user_logged_in)
def update_user_history(sender, user, **kwargs):
    user.last_logged_in = datetime.now().replace(tzinfo=utc)
    user.save(update_fields=['last_logged_in'])


class SignupPending(TemplateView):
    """
    Shown to the user after they sign up to tell them to confirm the link in their emails
    """

    template_name = 'users/signup-pending.jinja'


signup_pending = SignupPending.as_view()


class UserSignUp(DFFormView):
    template_name = 'users/signup.jinja'
    form_class = UserSignupForm

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('dashboard')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        data = {k: v for k, v in form.cleaned_data.items() if k not in {'password1', 'password2', 'captcha'}}
        data['password'] = make_password(form.cleaned_data['password1'])
        key = generate_random_key()
        cache.set('signup-' + key, data, 86400 * 7)  # store in cache for 1 week
        # TODO: Send the email to the user to confirm signup
        confirm_link = reverse('signup-confirm', kwargs={'key': key})
        print(f'\n\nSignup confirm link: {confirm_link}\n\n')
        return redirect('signup-pending')


user_signup = UserSignUp.as_view()


def signup_confirm(request, key):
    cache_key = 'signup-' + key
    data = cache.get(cache_key)
    if data is None:
        messages.error(
            request,
            (
                'That link is invalid. Either it has been used already, or it has expired. '
                'You can create your account again from the sign up form'
            ),
        )
        return redirect('dashboard')
    cache.delete(cache_key)
    try:
        user = User.objects.create(**data)
    except IntegrityError:
        messages.error(
            request,
            'A user already exists with either that Email address or screen name. Please try signing up again',
        )
        return redirect('dashboard')
    else:
        dj_login(request, user)
        messages.success(request, 'Account successfully created.')
        return redirect(data.get('next') or '/')


class UserProfileUpdate:
    pass


class GMSignUp:
    pass


class GMProfileUpdate:
    pass

class UserUpdateTheme(LoginRequiredMixin, DFFormView):
    model = User   # The model that will be edited
    form_class = UserUpdateThemeForm  # The form that we'll insert into the template and validate with
    template_name = 'users/themes.jinja'  # Your bit

    def get_object(self, queryset=None):
        return self.request.user  

    def form_valid(self, form):
        theme = form.cleaned_data['theme']
        self.request.user.user_theme = theme  # Get the data from the form
        self.request.user.save()  # and save
        messages.success(self.request, 'Well done, you did good editing')  # Displaying the nice message to the user
        return redirect('dashboard')  # Not sure where you want to return the user to after, but this is where you say


user_update_theme = UserUpdateTheme.as_view()
