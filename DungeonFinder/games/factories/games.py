import factory

from DungeonFinder.games.models import Game
from DungeonFinder.users.factories.users import GameMasterFactory


class GameFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Game

    name = factory.Sequence(lambda n: f'Game {n}')
    description = 'The best game in the world'
    creator = factory.SubFactory(GameMasterFactory)
    max_players = 4
