from captcha.fields import ReCaptchaField
from django import forms
from django.conf import settings
from django.contrib.auth.password_validation import validate_password

from DungeonFinder.common.forms import DFForm, DFModelForm
from DungeonFinder.users.models import User


class NewPasswordField(forms.CharField):
    widget = forms.PasswordInput

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = None

    def widget_attrs(self, widget):
        return {'minlength': str(settings.PASSWORD_MIN_LENGTH)}

    def validate(self, value):
        super().validate(value)
        validate_password(value, user=self.user)


class SimplePasswordField(forms.CharField):
    widget = forms.PasswordInput


class UserSignupForm(DFModelForm):
    email = forms.EmailField(label='Email', widget=forms.EmailInput)
    password1 = NewPasswordField(
        label='Password',
        help_text=(
            f'Should be at least {settings.PASSWORD_MIN_LENGTH} characters long and '
            f'contain at least one letter and one number'
        ),
    )
    password2 = SimplePasswordField(label='Confirm password')
    first_name = forms.CharField(label='First name')
    last_name = forms.CharField(label='Last name')
    captcha = ReCaptchaField()

    def clean_email(self):
        return self.cleaned_data['email'].lower()

    def clean_password2(self):
        if (
            'password1' in self.cleaned_data
            and 'password2' in self.cleaned_data
            and self.cleaned_data['password1'] != self.cleaned_data['password2']
        ):
            raise forms.ValidationError('You must type the same password each time.')

    class Meta:
        model = User
        fields = 'email', 'first_name', 'last_name', 'screen_name'


class UserUpdateThemeForm(DFForm):
    themes = [
        ('theme-dark-red', 'Dark Red'),
        ('theme-dark-blue', 'Dark Blue'),
        ('theme-light-red', 'Light Red'),
        ('theme-light-blue', 'Light Blue'),
    ]
    theme = forms.ChoiceField(widget=forms.RadioSelect, choices=themes)


class UserProfileForm(DFModelForm):
    class Meta:
        model = User
        fields = 'first_name', 'last_name', 'screen_name', 'avatar'
