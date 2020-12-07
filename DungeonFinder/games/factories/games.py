import factory

from DungeonFinder.games.models import Game


class GameFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Game

    name = factory.Sequence(lambda n: f'Game {n}')
    description = 'The best game in the world'
