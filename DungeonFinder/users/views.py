from datetime import datetime

from django.contrib import messages
from django.contrib.auth import login as dj_login, user_logged_in
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.hashers import make_password
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.core.cache import cache
from django.core.exceptions import PermissionDenied
from django.db import IntegrityError
from django.dispatch import receiver
from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import DetailView, TemplateView
from pytz import utc

from DungeonFinder.common.views import DFEditView, DFFormView, DFView, generate_random_key
from DungeonFinder.messaging.emails import EmailRecipient, EmailTemplate, UserEmail, send_email
from DungeonFinder.users.forms import UserProfileForm, UserSignupForm, UserUpdateThemeForm
from DungeonFinder.users.models import GameMaster, User


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
        confirm_link = reverse('signup-confirm', kwargs={'key': key})
        send_email.delay(
            UserEmail(
                recipient=EmailRecipient(
                    email=data['email'],
                    first_name=data['first_name'],
                    last_name=data['last_name'],
                ),
                context={'confirm_link': confirm_link},
                template_type=EmailTemplate.TEMPLATE_SIGNUP,
            )
        )
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


class UserUpdateProfile(LoginRequiredMixin, DFEditView):
    model = User
    form_class = UserProfileForm
    template_name = 'users/profile-update.jinja'
    success_url = reverse_lazy('dashboard')

    def get_object(self, queryset=None):
        return self.request.user


edit_profile = UserUpdateProfile.as_view()


class UserProfile(DetailView):
    model = User
    template_name = 'users/profile.jinja'

    def get_object(self, queryset=None):
        return self.request.user


user_profile = UserProfile.as_view()


class GMSignUp:
    pass


class GMProfileUpdate:
    pass


class UserUpdateTheme(LoginRequiredMixin, DFFormView):
    model = User
    form_class = UserUpdateThemeForm
    template_name = 'users/themes.jinja'

    def get_object(self, queryset=None):
        return self.request.user

    def form_valid(self, form):
        theme = form.cleaned_data['theme']
        self.request.user.user_theme = theme  # Get the data from the form
        self.request.user.save()  # and save
        messages.success(self.request, 'Well done, you did good editing')  # Displaying the nice message to the user
        return redirect('dashboard')  # Not sure where you want to return the user to after, but this is where you say


user_update_theme = UserUpdateTheme.as_view()


class PlayerProfile(DFView, DetailView):
    model = User
    context_object_name = 'player'
    template_name = 'users/player-profile.jinja'
    slug_field = slug_url_kwarg = 'screen_name'

    def get_meta_title(self):
        return self.get_object().screen_name


player_profile = PlayerProfile.as_view()


class GameMasterProfile(DFView, DetailView):
    model = GameMaster
    template_name = 'users/gm-profile.jinja'
    slug_field = 'user__screen_name'
    slug_url_kwarg = 'screen_name'

    def get_meta_title(self):
        return self.get_object().user.screen_name


gm_profile = GameMasterProfile.as_view()
