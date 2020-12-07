from django.test import TestCase, Client
from datetime import datetime as dt

from django.urls import reverse
from pytz import utc

from DungeonFinder.common.test_helpers import AuthenticatedClient
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
        self.assertNotContains(r, 'I am authenticated')

        r = client.post(reverse('login'), data={'username': 'hystera@example.com', 'password': 'testing1'}, follow=True)
        self.assertRedirects(r, '/')
        self.assertContains(r, 'I am authenticated')
        self.assertNotContains(r, 'Login')
        assert User.objects.get(id=user.id).last_logged_in.date() == dt.now().date()

    def test_logout(self):
        client = AuthenticatedClient()
        assert client.user.is_authenticated
        r = client.get('/')
        self.assertContains(r, 'I am authenticated')
        r = client.post(reverse('logout'), follow=True)
        self.assertNotContains(r, 'I am authenticated')
        self.assertRedirects(r, '/')

    def test_unauthed_header_content(self):
        pass

    def test_authed_header_content(self):
        pass
