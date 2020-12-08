from django.test import TestCase
from django.urls import reverse

from DungeonFinder.games.factories.games import GameFactory


class GamesListTestCase(TestCase):
    def test_games_list(self):
        r = self.client.get(reverse('games-data'))
        self.assertNotContains(r, 'Amazagame')
        GameFactory(name='Amazagame')
        r = self.client.get(reverse('games-data'))
        self.assertContains(r, 'Amazagame')
