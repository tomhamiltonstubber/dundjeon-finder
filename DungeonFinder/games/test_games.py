from django.test import TestCase
from django.urls import reverse

from DungeonFinder.games.factories.games import GameFactory


class GamesListTestCase(TestCase):
    def test_games_list(self):
        r = self.client.get(reverse('games-list'))
        self.assertNotContains(r, 'Amazagame')
        GameFactory(name='Amazagame')
        r = self.client.get(reverse('games-list'))
        self.assertContains(r, 'Amazagame')

    def test_list_filtered(self):
        pass
