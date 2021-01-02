from django.test import TestCase
from django.urls import reverse

from DungeonFinder.common.test_helpers import AuthenticatedClient
from DungeonFinder.games.factories.games import CampaignFactory
from DungeonFinder.messaging.factories.messages import MessageFactory
from DungeonFinder.users.factories.users import GameMasterFactory, UserFactory


class CampMessageTestCase(TestCase):
    def setUp(self):
        self.player = UserFactory()
        self.gm = GameMasterFactory()
        self.campaign = CampaignFactory(creator=self.gm)
        self.campaign.players.add(self.player)
        self.player_client = AuthenticatedClient(user=self.player)
        self.gm_client = AuthenticatedClient(user=self.gm.user)
        self.admin = UserFactory(is_admin=True)
        self.admin_client = AuthenticatedClient(user=self.admin)
        self.oplayer_client = AuthenticatedClient()
        self.feed_url = reverse('camp-message-feed', args=[self.campaign.pk])
        self.add_msg = reverse('camp-message-add', args=[self.campaign.pk])

    def test_create_message(self):
        r = self.player_client.get(self.feed_url)
        self.assertNotContains(r, 'I am a message')
        r = self.player_client.post(self.add_msg, {'text': 'I am a message'})
        assert r.json() == {'count': 1}
        r = self.player_client.get(self.feed_url)
        self.assertContains(r, 'I am a message')

    def test_create_message_gm(self):
        r = self.gm_client.get(self.feed_url)
        self.assertNotContains(r, 'I am a message')
        r = self.gm_client.post(self.add_msg, {'text': 'I am a message'})
        assert r.json() == {'count': 1}
        r = self.gm_client.get(self.feed_url)
        self.assertContains(r, 'I am a message')

    def test_create_message_admin(self):
        r = self.admin_client.get(self.feed_url)
        self.assertNotContains(r, 'I am a message')
        r = self.admin_client.post(self.add_msg, {'text': 'I am a message'})
        assert r.json() == {'count': 1}
        r = self.admin_client.get(self.feed_url)
        self.assertContains(r, 'I am a message')

    def test_create_message_wrong_player(self):
        MessageFactory(campaign=self.campaign, author=self.player, text='I am a message')
        r = self.oplayer_client.get(self.feed_url)
        assert r.json() == []
        r = self.oplayer_client.post(self.add_msg, {'text': 'I am another message'})
        assert r.status_code == 404

    def test_create_message_bad_form(self):
        r = self.player_client.post(self.add_msg, {'Foo': 'Bar'})
        assert r.json() == {'text': ['This field is required.']}
        assert r.status_code == 400

    def test_edit_message(self):
        m = MessageFactory(campaign=self.campaign, author=self.player, text='I am a message')
        r = self.player_client.get(reverse('message-edit', args=[m.pk]))
        assert r.status_code == 405
        r = self.player_client.post(reverse('message-edit', args=[m.pk]), {'text': 'I am no longer a message'})
        self.assertRedirects(r, self.campaign.get_absolute_url())
        r = self.player_client.get(self.feed_url)
        self.assertNotContains(r, 'I am a message')
        self.assertContains(r, 'I am no longer a message')

    def test_edit_message_gm(self):
        m = MessageFactory(campaign=self.campaign, author=self.gm.user, text='I am a message')
        r = self.gm_client.post(reverse('message-edit', args=[m.pk]), {'text': 'I am no longer a message'})
        self.assertRedirects(r, self.campaign.get_absolute_url())
        r = self.gm_client.get(self.feed_url)
        self.assertNotContains(r, 'I am a message')
        self.assertContains(r, 'I am no longer a message')

    def test_edit_message_bad_form(self):
        m = MessageFactory(campaign=self.campaign, author=self.player, text='I am a message')
        r = self.player_client.post(reverse('message-edit', args=[m.pk]), {'Foo': 'Bar'})
        assert r.json() == {'text': ['This field is required.']}
        assert r.status_code == 400

    def test_edit_message_wrong_author(self):
        m = MessageFactory(campaign=self.campaign, author=self.player, text='I am a message')
        r = self.oplayer_client.post(reverse('message-edit', args=[m.pk]), {'Foo': 'Bar'})
        assert r.status_code == 404

    def test_edit_message_admin(self):
        m = MessageFactory(campaign=self.campaign, author=self.gm.user, text='I am a message')
        r = self.admin_client.post(reverse('message-edit', args=[m.pk]), {'text': 'I am no longer a message'})
        self.assertRedirects(r, self.campaign.get_absolute_url())
        r = self.admin_client.get(self.feed_url)
        self.assertNotContains(r, 'I am a message')
        self.assertContains(r, 'I am no longer a message')

    def test_delete_message(self):
        m = MessageFactory(campaign=self.campaign, author=self.player, text='I am a message')
        r = self.player_client.post(reverse('message-delete', args=[m.pk]))
        self.assertRedirects(r, self.campaign.get_absolute_url())
        r = self.player_client.get(self.feed_url)
        self.assertNotContains(r, 'I am a message')

    def test_delete_message_gm(self):
        m = MessageFactory(campaign=self.campaign, author=self.gm.user, text='I am a message')
        r = self.gm_client.post(reverse('message-delete', args=[m.pk]))
        self.assertRedirects(r, self.campaign.get_absolute_url())
        r = self.gm_client.get(self.feed_url)
        self.assertNotContains(r, 'I am a message')

    def test_delete_message_admin(self):
        m = MessageFactory(campaign=self.campaign, author=self.player, text='I am a message')
        r = self.admin_client.post(reverse('message-delete', args=[m.pk]))
        self.assertRedirects(r, self.campaign.get_absolute_url())
        r = self.admin_client.get(self.feed_url)
        self.assertNotContains(r, 'I am a message')

    def test_delete_message_wrong_author(self):
        m = MessageFactory(campaign=self.campaign, author=self.player, text='I am a message')
        r = self.oplayer_client.post(reverse('message-delete', args=[m.pk]))
        assert r.status_code == 404

    def test_message_feed(self):
        m = MessageFactory(campaign=self.campaign, author=self.player, text='I am a message')
        m2 = MessageFactory(campaign=self.campaign, author=self.gm.user, text='I am another message')
        r = self.player_client.get(self.feed_url)
        assert r.json() == [
            {
                'id': m2.id,
                'text': 'I am another message',
                'timestamp': m2.timestamp.strftime('%Y-%m-%dT%H:%M'),
                'author': self.gm.user.screen_name,
                'gm_message': True,
            },
            {
                'id': m.id,
                'text': 'I am a message',
                'timestamp': m.timestamp.strftime('%Y-%m-%dT%H:%M'),
                'author': self.player.screen_name,
                'gm_message': False,
            },
        ]

    def test_message_feed_no_new_messages(self):
        m = MessageFactory(campaign=self.campaign, author=self.player, text='I am a message')
        m2 = MessageFactory(campaign=self.campaign, author=self.gm.user, text='I am another message')
        r = self.player_client.get(self.feed_url + '?c=1')
        assert r.json() == [
            {
                'id': m2.id,
                'text': 'I am another message',
                'timestamp': m2.timestamp.strftime('%Y-%m-%dT%H:%M'),
                'author': self.gm.user.screen_name,
                'gm_message': True,
            },
            {
                'id': m.id,
                'text': 'I am a message',
                'timestamp': m.timestamp.strftime('%Y-%m-%dT%H:%M'),
                'author': self.player.screen_name,
                'gm_message': False,
            },
        ]
        r = self.player_client.get(self.feed_url + '?c=2')
        assert r.json() == []

    def test_message_feed_bad_count(self):
        m = MessageFactory(campaign=self.campaign, author=self.player, text='I am a message')
        m2 = MessageFactory(campaign=self.campaign, author=self.gm.user, text='I am another message')
        r = self.player_client.get(self.feed_url)
        assert r.json() == [
            {
                'id': m2.id,
                'text': 'I am another message',
                'timestamp': m2.timestamp.strftime('%Y-%m-%dT%H:%M'),
                'author': self.gm.user.screen_name,
                'gm_message': True,
            },
            {
                'id': m.id,
                'text': 'I am a message',
                'timestamp': m.timestamp.strftime('%Y-%m-%dT%H:%M'),
                'author': self.player.screen_name,
                'gm_message': False,
            },
        ]
        r = self.player_client.get(self.feed_url + '?c=foo')
        assert r.json() == []
