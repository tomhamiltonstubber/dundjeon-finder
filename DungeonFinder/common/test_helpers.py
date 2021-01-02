from django.test import Client

from DungeonFinder.users.models import GameMaster, User

num_lu = {
    1: 'One',
    2: 'Two',
    3: 'Three',
    4: 'Four',
    5: 'Five',
    6: 'Six',
    7: 'Seven',
    8: 'Eight',
    9: 'Nine',
}


class AuthenticatedClient(Client):
    def __init__(self, is_gm=True, user=None):
        super().__init__()
        if not user:
            if is_gm:
                user_cnt = User.objects.filter(gamemaster__isnull=False, is_admin=False).count()
                num_str = num_lu[user_cnt + 1]
                kwargs = {
                    'first_name': 'Game',
                    'last_name': f'Master {num_str}',
                    'email': f'game_master_{num_str.lower()}@example.com',
                    'screen_name': f'game_master_{num_str.lower()}',
                }
            else:
                user_cnt = User.objects.filter(gamemaster__isnull=True, is_admin=False).count()
                num_str = num_lu[user_cnt + 1]
                kwargs = {
                    'first_name': 'Player',
                    'last_name': num_str,
                    'email': f'player_{num_str.lower()}@example.com',
                    'screen_name': f'player_{num_str.lower()}',
                }
            user = User.objects.create_user(password='testing', **kwargs)
            if is_gm:
                GameMaster.objects.create(user=user)
        logged_in = self.login(username=user.email, password='testing')
        if not logged_in:  # pragma: no cover
            raise RuntimeError('Not logged in')
        self.user = User.objects.get(pk=self.session['_auth_user_id'])
