from datetime import datetime as dt
from unittest.mock import patch

from captcha.client import RecaptchaResponse
from django.core.cache import cache
from django.test import Client, TestCase, TransactionTestCase, override_settings
from django.urls import reverse
from pytz import utc

from DungeonFinder.common.test_helpers import AuthenticatedClient
from DungeonFinder.users.factories.users import UserFactory
from DungeonFinder.users.models import User


class UserAuthTestCase(TestCase):
    def test_login(self):
        user = User.objects.create_user(
            first_name='Hystera',
            last_name='Died',
            email='hystera@example.com',
        )
        user.set_password('testing1')
        user.save()
        assert user.last_logged_in == dt(2020, 1, 1, tzinfo=utc)
        client = Client()
        r = self.client.get(reverse('login'))
        self.assertContains(r, 'Login')

        r = client.post(reverse('login'), data={'username': 'hystera@example.com', 'password': 'testing2'})
        assert r.status_code == 200
        self.assertNotContains(r, 'Logout')

        r = client.post(reverse('login'), data={'username': 'hystera@example.com', 'password': 'testing1'}, follow=True)
        self.assertRedirects(r, '/')
        self.assertContains(r, 'Sign out')
        self.assertNotContains(r, 'Login')
        assert User.objects.get(id=user.id).last_logged_in.date() == dt.now().date()

    def test_logout(self):
        client = AuthenticatedClient()
        assert client.user.is_authenticated
        r = client.get('/')
        self.assertContains(r, 'Sign out')
        r = client.post(reverse('logout'), follow=True)
        self.assertNotContains(r, 'Sign out')
        self.assertRedirects(r, '/')


@override_settings(RECAPTCHA_TESTING=True)
class UserSignupTestCase(TransactionTestCase):
    def setUp(self):
        cache.clear()
        self.signup_url = reverse('signup')

    @patch('captcha.fields.client.submit')
    def test_user_signup(self, mock_cap):
        mock_cap.return_value = RecaptchaResponse(is_valid=True)
        r = self.client.get(self.signup_url)
        self.assertContains(r, 'Sign Up')
        r = self.client.post(
            self.signup_url,
            data={
                'email': 'foo@example.com',
                'first_name': 'New',
                'last_name': 'Player',
                'password1': 'fooexample1',
                'password2': 'fooexample1',
                'screen_name': 'FooPlayer1',
                'g-recaptcha-response': 'PASSED',
            },
            follow=True,
        )
        self.assertRedirects(r, reverse('signup-pending'))
        self.assertContains(r, 'Confirm your account')
        key = cache.keys('signup-*')[0]
        data = cache.get(key)
        data.pop('password')
        assert data == {
            'email': 'foo@example.com',
            'first_name': 'New',
            'last_name': 'Player',
            'screen_name': 'FooPlayer1',
        }

    @patch('captcha.fields.client.submit')
    def test_user_signup_wrong_password(self, mock_cap):
        mock_cap.return_value = RecaptchaResponse(is_valid=True)
        r = self.client.get(self.signup_url)
        self.assertContains(r, 'Sign Up')
        r = self.client.post(
            self.signup_url,
            data={
                'email': 'foo@example.com',
                'first_name': 'New',
                'last_name': 'Player',
                'password1': 'fooexample1',
                'password2': 'fooexample2',
                'screen_name': 'FooPlayer1',
                'g-recaptcha-response': 'PASSED',
            },
        )
        self.assertContains(r, 'You must type the same password each time')
        r = self.client.post(
            self.signup_url,
            data={
                'email': 'foo@example.com',
                'first_name': 'New',
                'last_name': 'Player',
                'password1': 'password1',
                'password2': 'password',
                'screen_name': 'FooPlayer1',
                'g-recaptcha-response': 'PASSED',
            },
        )
        self.assertContains(r, 'too common')

    def test_user_signup_logged_in(self):
        r = AuthenticatedClient().get(self.signup_url)
        self.assertRedirects(r, reverse('dashboard'))

    @patch('captcha.fields.client.submit')
    def test_user_signup_duplicate_screen_name(self, mock_cap):
        mock_cap.return_value = RecaptchaResponse(is_valid=True)
        r = self.client.get(self.signup_url)
        self.assertContains(r, 'Sign Up')
        UserFactory(screen_name='FooScreenName')
        r = self.client.post(
            self.signup_url,
            data={
                'email': 'foo@example.com',
                'first_name': 'New',
                'last_name': 'Player',
                'password1': 'fooexample1',
                'password2': 'fooexample1',
                'screen_name': 'FooScreenName',
                'g-recaptcha-response': 'PASSED',
            },
        )
        self.assertContains(r, 'A user with that screen name already exists.')

    @patch('captcha.fields.client.submit')
    def test_user_signup_duplicate_email(self, mock_cap):
        mock_cap.return_value = RecaptchaResponse(is_valid=True)
        r = self.client.get(self.signup_url)
        self.assertContains(r, 'Sign Up')
        UserFactory(email='foo@example.com')
        r = self.client.post(
            self.signup_url,
            data={
                'email': 'foo@example.com',
                'first_name': 'New',
                'last_name': 'Player',
                'password1': 'fooexample1',
                'password2': 'fooexample1',
                'screen_name': 'FooScreenName',
                'g-recaptcha-response': 'PASSED',
            },
        )
        self.assertContains(r, 'User with this Email Address already exists.')

    @patch('captcha.fields.client.submit')
    def test_user_confirm_signup(self, mock_cap):
        mock_cap.return_value = RecaptchaResponse(is_valid=True)
        r = self.client.get(self.signup_url)
        self.assertContains(r, 'Sign Up')
        r = self.client.post(
            self.signup_url,
            data={
                'email': 'foo@example.com',
                'first_name': 'New',
                'last_name': 'Player',
                'password1': 'fooexample1',
                'password2': 'fooexample1',
                'screen_name': 'FooPlayer1',
                'g-recaptcha-response': 'PASSED',
            },
            follow=True,
        )
        self.assertRedirects(r, reverse('signup-pending'))
        self.assertContains(r, 'Confirm your account')
        key = cache.keys('signup-*')[0].split('-')[1]
        r = self.client.get(reverse('signup-confirm', args=[key]))
        self.assertRedirects(r, reverse('dashboard'))
        user = User.objects.get()
        assert user.email == 'foo@example.com'
        assert user.first_name == 'New'
        assert user.last_name == 'Player'
        assert user.screen_name == 'FooPlayer1'

    @patch('captcha.fields.client.submit')
    def test_user_confirm_duplicate_screen_name(self, mock_cap):
        mock_cap.return_value = RecaptchaResponse(is_valid=True)
        r = self.client.get(self.signup_url)
        self.assertContains(r, 'Sign Up')
        r = self.client.post(
            self.signup_url,
            data={
                'email': 'foo@example.com',
                'first_name': 'New',
                'last_name': 'Player',
                'password1': 'fooexample1',
                'password2': 'fooexample1',
                'screen_name': 'FooScreenName',
                'g-recaptcha-response': 'PASSED',
            },
            follow=True,
        )
        self.assertRedirects(r, reverse('signup-pending'))
        self.assertContains(r, 'Confirm your account')

        UserFactory(screen_name='FooScreenName')

        key = cache.keys('signup-*')[0].split('-')[1]
        r = self.client.get(reverse('signup-confirm', args=[key]))
        self.assertRedirects(r, reverse('dashboard'))
        assert User.objects.count() == 1

    @patch('captcha.fields.client.submit')
    def test_user_confirm_duplicate_email(self, mock_cap):
        mock_cap.return_value = RecaptchaResponse(is_valid=True)
        r = self.client.get(self.signup_url)
        self.assertContains(r, 'Sign Up')
        r = self.client.post(
            self.signup_url,
            data={
                'email': 'foo@example.com',
                'first_name': 'New',
                'last_name': 'Player',
                'password1': 'fooexample1',
                'password2': 'fooexample1',
                'screen_name': 'FooScreenName',
                'g-recaptcha-response': 'PASSED',
            },
            follow=True,
        )
        self.assertRedirects(r, reverse('signup-pending'))
        self.assertContains(r, 'Confirm your account')

        UserFactory(email='foo@example.com')

        key = cache.keys('signup-*')[0].split('-')[1]
        r = self.client.get(reverse('signup-confirm', args=[key]))
        self.assertRedirects(r, reverse('dashboard'))
        assert User.objects.count() == 1
