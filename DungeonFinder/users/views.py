from datetime import datetime

from django.contrib.auth import user_logged_in
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.views import LoginView
from django.core.exceptions import PermissionDenied
from django.dispatch import receiver
from django.urls import reverse


class GMRequestMixin:
    def dispatch(self, request, *args, **kwargs):
        if not (request.user.is_authenticated and request.user.is_gm):
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)


class Login(LoginView):
    template_name = 'auth/login.jinja'
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
    user.last_logged_in = datetime.now()
    user.save(update_fields=['last_logged_in'])


class UserSignUp:
    pass


class UserProfileUpdate:
    pass


class GMSignUp:
    pass


class GMProfileUpdate:
    pass
