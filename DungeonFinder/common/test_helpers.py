from django.test import Client

from DungeonFinder.users.models import User


class AuthenticatedClient(Client):
    def __init__(self):
        super().__init__()
        self.user = User.objects.create_user(
            first_name='Hystera',
            last_name='Died',
            email='hystera@example.com',
            password='testing',
        )
        logged_in = self.login(username=self.user.email, password='testing')
        if not logged_in:  # pragma: no cover
            raise RuntimeError('Not logged in')
        self.user = User.objects.get(pk=self.session['_auth_user_id'])
