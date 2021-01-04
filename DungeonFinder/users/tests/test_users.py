import os
from datetime import datetime as dt
from unittest.mock import patch

from captcha.client import RecaptchaResponse
from django.conf import settings
from django.core.cache import cache
from django.core.files import File
from django.core.files.temp import NamedTemporaryFile
from django.test import Client, TestCase, TransactionTestCase, override_settings
from django.urls import reverse
from pytz import utc

from DungeonFinder.actions.models import Action
from DungeonFinder.common.test_helpers import AuthenticatedClient
from DungeonFinder.users.factories.users import GameMasterFactory, UserFactory
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
        user = User.objects.get(id=user.id)
        assert user.last_logged_in.date() == dt.now().date()
        action = Action.objects.get()
        assert action.action_type == Action.ACTION_LOGIN
        assert action.actor == action.target_user == user

    def test_logout(self):
        client = AuthenticatedClient()
        assert client.user.is_authenticated
        r = client.get('/')
        self.assertContains(r, 'Sign out')
        r = client.post(reverse('logout'), follow=True)
        self.assertNotContains(r, 'Sign out')
        self.assertRedirects(r, '/')
        assert Action.objects.get(action_type=Action.ACTION_LOGOUT).actor == client.user


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
        assert not Action.objects.exists()

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
        assert not Action.objects.exists()

    def test_user_signup_logged_in(self):
        cli = AuthenticatedClient()
        r = cli.get(self.signup_url)
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
        action = Action.objects.get(action_type=Action.ACTION_SIGNUP)
        assert action.target_user == action.actory == User.objects.get()

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


class UserFormTest(TestCase):
    def setUp(self):
        self.user = UserFactory(screen_name='Kazooey')
        self.client = AuthenticatedClient(user=self.user)
        self.rurl = reverse('profile-edit')

    def _get_temp_image(self, size_str, file_type):
        temp_image = NamedTemporaryFile(delete=True)
        img_path = os.path.join(settings.BASE_DIR, f'static/tests/{size_str}.{file_type}')
        temp_image.write(open(img_path, 'rb').read())
        temp_image.flush()
        return temp_image

    def test_edit_profile(self):
        r = self.client.get(reverse('dashboard'))
        self.assertContains(r, 'Kazooey')
        self.assertNotContains(r, 'Banjo')
        r = self.client.get(self.rurl)
        self.assertContains(r, 'Kazooey')
        self.assertNotContains(r, 'Banjo')
        r = self.client.post(self.rurl, {'screen_name': 'Banjo', 'last_name': 'Foo', 'first_name': 'test'}, follow=True)
        self.assertRedirects(r, reverse('dashboard'))
        self.assertContains(r, 'Banjo')
        self.assertNotContains(r, 'Kazooey')
        assert User.objects.get(pk=self.user.pk).screen_name == 'Banjo'
        assert Action.objects.count() == 1
        action = Action.objects.get(action_type=Action.ACTION_EDIT_PROFILE)
        assert action.target_user == action.actor == User.objects.get()

    def test_add_avatar(self):
        img = File(self._get_temp_image('300x300', file_type='png'), name='test.png')
        self.user.avatar = img
        self.user.save()
        user = User.objects.get()
        assert user.avatar
        r = self.client.get(reverse('profile'))
        self.assertContains(r, f'src="{user.avatar.url}.200x200_q85_crop.jpg"')


class PlayerProfileTestCase(TestCase):
    def test_user_profile(self):
        player = UserFactory()
        r = self.client.get(player.get_profile_url())
        self.assertContains(r, player.screen_name)


class GMProfileTestCase(TestCase):
    def test_gm_profile(self):
        gm = GameMasterFactory()
        r = self.client.get(gm.get_profile_url())
        self.assertContains(r, gm.user.screen_name)
