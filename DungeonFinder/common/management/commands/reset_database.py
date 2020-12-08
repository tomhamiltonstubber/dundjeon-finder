from django.core.management import BaseCommand, call_command
from django.db import connection

from DungeonFinder.games.models import Game
from DungeonFinder.users.models import User, GameMaster


class Command(BaseCommand):
    help = 'Reset database and create demo data'

    def handle(self, **kwargs):
        if input('Are you sure you want to DESTROY ALL DATA irreversibly? [yes/NO] ') != 'yes':
            print('Cancelled')
            return

        cur = connection.cursor()
        cur.execute('DROP SCHEMA public CASCADE;')
        cur.execute('CREATE SCHEMA public;')

        call_command('migrate', run_syncdb=True)
        # Creating 3 Users, 1 GM, 1 Super admin, and 3 Games. The GM has the login details provided.
        p1 = User.objects.create_user(
            first_name='Pedro',
            last_name='Negro',
            password='testing1',
            email='player1@example.com',
            screen_name='PedroNegro',
        )
        p2 = User.objects.create_user(
            first_name='Buddy',
            last_name='Finn',
            password='testing1',
            email='player2@example.com',
            screen_name='BuddyFinn',
        )
        p3 = User.objects.create_user(
            first_name='Lapy',
            last_name='Lowwlander',
            password='testing1',
            email='player3@example.com',
            screen_name='LapyLowwlander',
        )

        gm_user = User.objects.create_user(
            first_name='Syvas',
            last_name='Lives',
            password='testing1',
            email='gamemaster@example.com',
            screen_name='SyvasLives',
        )
        gm = GameMaster.objects.create(user=gm_user)

        User.objects.create_superuser(
            first_name='Hystera',
            last_name='Dies',
            password='testing1',
            screen_name='HysteraDies',
            email='admin@example.com',
        )

        game1 = Game.objects.create(
            name='Mines of Phandelver', description='A finished first game', creator=gm, max_players=4
        )
        game1.players.add(p1)
        game1.players.add(p2)
        game1.players.add(p3)
        game2 = Game.objects.create(
            name='Into the Abyss', description='A current ongoing game', creator=gm, max_players=3
        )
        game2.players.add(p2, p3)
        game3 = Game.objects.create(name='Curse of Strahd', description='A future game', creator=gm, max_players=5)
        game3.players.add(p3)
        print(
            '\n    Created 3 players, 1 GM and 3 games.\n '
            '   You can login using [player1/2/3 or gm or admin]@example.com with password testing1\n'
        )
