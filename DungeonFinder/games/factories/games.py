import factory

from DungeonFinder.games.models import Campaign
from DungeonFinder.users.factories.users import GameMasterFactory


class CampaignFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Campaign

    name = factory.Sequence(lambda n: f'Game {n}')
    description = 'The best game in the world'
    creator = factory.SubFactory(GameMasterFactory)
    max_players = 4
