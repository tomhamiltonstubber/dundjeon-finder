import datetime
from decimal import Decimal

from django.test import TestCase
from django.urls import reverse, reverse_lazy
from pytz import utc

from DungeonFinder.common.test_helpers import AuthenticatedClient
from DungeonFinder.games.factories.games import CampaignFactory
from DungeonFinder.games.models import Campaign
from DungeonFinder.users.factories.users import UserFactory


class CampsListTestCase(TestCase):
    avail_data_url = reverse_lazy('avail-campaigns-data')

    def test_camps_list_view(self):
        r = self.client.get(reverse('avail-campaign-list'))
        self.assertContains(r, reverse('avail-campaigns-data'))

    def test_camps_list_simple(self):
        r = self.client.get(reverse('avail-campaigns-data'))
        self.assertNotContains(r, 'Amazagame')
        CampaignFactory(name='Amazagame')
        r = self.client.get(reverse('avail-campaigns-data'))
        self.assertContains(r, 'Amazagame')

    def test_show_only_available(self):
        CampaignFactory(status=Campaign.STATUS_PENDING, name='Camp1')
        CampaignFactory(status=Campaign.STATUS_IN_PROGRESS, name='Camp2')
        CampaignFactory(status=Campaign.STATUS_COLD, name='Camp3')
        CampaignFactory(status=Campaign.STATUS_FINISHED, name='Camp4')
        CampaignFactory(status=Campaign.STATUS_IN_PROGRESS, accepting_players=False, name='Camp5')
        player = UserFactory()
        camp6 = CampaignFactory(status=Campaign.STATUS_IN_PROGRESS, max_players=1, name='Camp6')
        camp6.players.add(player)
        camp7 = CampaignFactory(status=Campaign.STATUS_IN_PROGRESS, max_players=2, name='Camp7')
        camp7.players.add(player)

        r = self.client.get(self.avail_data_url)
        self.assertContains(r, 'Camp1')
        self.assertContains(r, 'Camp2')
        self.assertNotContains(r, 'Camp3')
        self.assertNotContains(r, 'Camp4')
        self.assertNotContains(r, 'Camp5')
        self.assertNotContains(r, 'Camp6')
        self.assertContains(r, 'Camp7')

    def test_camps_list_filter_next_game_dt(self):
        CampaignFactory(next_game_dt=datetime.datetime(2020, 1, 10, tzinfo=utc), name='Camp1')
        CampaignFactory(next_game_dt=datetime.datetime(2020, 1, 15, tzinfo=utc), name='Camp2')
        CampaignFactory(next_game_dt=None, name='Camp3')

        r = self.client.get(self.avail_data_url)
        self.assertContains(r, 'Camp1')
        self.assertContains(r, 'Camp2')
        self.assertContains(r, 'Camp3')

        r = self.client.get(self.avail_data_url, {'next_game_from': datetime.date(2020, 1, 12).strftime('%Y-%m-%d')})
        self.assertNotContains(r, 'Camp1')
        self.assertContains(r, 'Camp2')
        self.assertNotContains(r, 'Camp3')

        r = self.client.get(self.avail_data_url, {'next_game_to': datetime.date(2020, 1, 12).strftime('%Y-%m-%d')})
        self.assertContains(r, 'Camp1')
        self.assertNotContains(r, 'Camp2')
        self.assertNotContains(r, 'Camp3')

    def test_camps_list_filter_pps(self):
        CampaignFactory(price_per_session=Decimal('4.5'), name='Camp1')
        CampaignFactory(price_per_session=10, name='Camp2')
        CampaignFactory(price_per_session=None, name='Camp3')

        r = self.client.get(self.avail_data_url)
        self.assertContains(r, 'Camp1')
        self.assertContains(r, 'Camp2')
        self.assertContains(r, 'Camp3')

        r = self.client.get(self.avail_data_url, {'price_per_session_from': '5'})
        self.assertNotContains(r, 'Camp1')
        self.assertContains(r, 'Camp2')
        self.assertNotContains(r, 'Camp3')

        r = self.client.get(self.avail_data_url, {'price_per_session_to': 5})
        self.assertContains(r, 'Camp1')
        self.assertNotContains(r, 'Camp2')
        self.assertNotContains(r, 'Camp3')

    def test_camps_list_filter_campaign_type(self):
        CampaignFactory(campaign_type=Campaign.TYPE_MODULAR, name='Camp1')
        CampaignFactory(campaign_type=Campaign.TYPE_HOMEBREW, name='Camp2')
        CampaignFactory(campaign_type=Campaign.TYPE_SOURCE_BOOK, name='Camp3')

        r = self.client.get(self.avail_data_url)
        self.assertContains(r, 'Camp1')
        self.assertContains(r, 'Camp2')
        self.assertContains(r, 'Camp3')

        r = self.client.get(self.avail_data_url, {'campaign_type': Campaign.TYPE_HOMEBREW})
        self.assertNotContains(r, 'Camp1')
        self.assertContains(r, 'Camp2')
        self.assertNotContains(r, 'Camp3')

    def test_camps_list_filter_rpl(self):
        CampaignFactory(role_play_level=Campaign.RP_ANY, name='Camp1')
        CampaignFactory(role_play_level=Campaign.RP_LIGHT, name='Camp2')
        CampaignFactory(role_play_level=Campaign.RP_HEAVY, name='Camp3')

        r = self.client.get(self.avail_data_url)
        self.assertContains(r, 'Camp1')
        self.assertContains(r, 'Camp2')
        self.assertContains(r, 'Camp3')

        r = self.client.get(self.avail_data_url, {'role_play_level': Campaign.RP_ANY})
        self.assertContains(r, 'Camp1')
        self.assertContains(r, 'Camp2')
        self.assertContains(r, 'Camp3')

        r = self.client.get(self.avail_data_url, {'role_play_level': Campaign.RP_HEAVY})
        self.assertNotContains(r, 'Camp1')
        self.assertNotContains(r, 'Camp2')
        self.assertContains(r, 'Camp3')

    def test_camps_list_filter_exclude_mature(self):
        CampaignFactory(mature_content=True, name='Camp1')
        CampaignFactory(mature_content=False, name='Camp2')

        r = self.client.get(self.avail_data_url)
        self.assertContains(r, 'Camp1')
        self.assertContains(r, 'Camp2')

        r = self.client.get(self.avail_data_url, {'exclude_mature_content': True})
        self.assertNotContains(r, 'Camp1')
        self.assertContains(r, 'Camp2')


class CampEditTestCase(TestCase):
    def setUp(self):
        self.player_client = AuthenticatedClient(is_gm=False)
        self.gm_client = AuthenticatedClient()

    def test_add_camp_not_gm(self):
        r = self.client.get(reverse('campaign-create'))
        self.assertRedirects(r, reverse('avail-campaign-list'))
        r = self.player_client.get(reverse('campaign-create'))
        self.assertRedirects(r, reverse('avail-campaign-list'))

    def test_add_camp(self):
        r = self.gm_client.get(reverse('campaign-create'))
        self.assertContains(r, 'Accepting players')
        data = {
            'name': 'A new campaign',
            'accepting_players': True,
            'beginners_welcome': True,
            'campaign_type': Campaign.TYPE_MODULAR,
            'description': 'A new new campaign',
            'mature_content': True,
            'max_players': 2,
            'next_game_dt': datetime.datetime(2020, 10, 1, 9).strftime('%Y-%m-%dT%H:%M'),
            'price_per_session': '3.45',
            'role_play_level': Campaign.RP_HEAVY,
        }
        r = self.gm_client.post(reverse('campaign-create'), data)
        camp = Campaign.objects.get()
        self.assertRedirects(r, camp.get_absolute_url())
        assert camp.name == 'A new campaign'
        assert camp.accepting_players
        assert camp.beginners_welcome
        assert camp.campaign_type == Campaign.TYPE_MODULAR
        assert camp.description == 'A new new campaign'
        assert camp.max_players == 2
        assert camp.mature_content
        assert camp.status == Campaign.STATUS_PENDING
        assert camp.next_game_dt == datetime.datetime(2020, 10, 1, 9, tzinfo=utc)
        assert camp.price_per_session == Decimal('3.45')
        assert camp.role_play_level == Campaign.RP_HEAVY

    def test_edit_camp(self):
        gm = self.gm_client.user.gamemaster
        camp = CampaignFactory(creator=gm, name='FooBar')
        r = self.gm_client.get(reverse('campaign-edit', args=[camp.pk]))
        self.assertContains(r, 'FooBar')
        r = self.gm_client.post(
            reverse('campaign-edit', args=[camp.pk]),
            data={
                'name': 'A new campaign',
                'accepting_players': True,
                'beginners_welcome': True,
                'campaign_type': Campaign.TYPE_MODULAR,
                'description': 'A new new campaign',
                'mature_content': True,
                'max_players': 2,
                'next_game_dt': datetime.datetime(2020, 10, 1, 9).strftime('%Y-%m-%dT%H:%M'),
                'price_per_session': '3.45',
                'role_play_level': Campaign.RP_HEAVY,
            },
        )
        camp = Campaign.objects.get()
        self.assertRedirects(r, camp.get_absolute_url())
        assert camp.name == 'A new campaign'
        assert camp.accepting_players
        assert camp.beginners_welcome
        assert camp.campaign_type == Campaign.TYPE_MODULAR
        assert camp.description == 'A new new campaign'
        assert camp.max_players == 2
        assert camp.mature_content
        assert camp.status == Campaign.STATUS_PENDING
        assert camp.next_game_dt == datetime.datetime(2020, 10, 1, 9, tzinfo=utc)
        assert camp.price_per_session == Decimal('3.45')
        assert camp.role_play_level == Campaign.RP_HEAVY

    def test_edit_camp_not_gm(self):
        player = self.player_client.user
        camp = CampaignFactory(name='FooBar')
        camp.players.add(player)
        r = self.player_client.get(reverse('campaign-edit', args=[camp.pk]))
        assert r.status_code == 404
        r = self.gm_client.get(reverse('campaign-edit', args=[camp.pk]))
        assert r.status_code == 404

    def test_delete_camp(self):
        camp = CampaignFactory(name='FooBar', creator=self.gm_client.user.gamemaster)
        r = self.player_client.post(reverse('campaign-delete', args=[camp.pk]))
        assert r.status_code == 404
        r = self.gm_client.post(reverse('campaign-delete', args=[camp.pk]))
        self.assertRedirects(r, reverse('avail-campaign-list'))
        assert not Campaign.objects.exists()

    def test_change_camp_status(self):
        camp = CampaignFactory(
            name='FooBar', creator=self.gm_client.user.gamemaster, status=Campaign.STATUS_IN_PROGRESS
        )
        assert Campaign.objects.get().status == Campaign.STATUS_IN_PROGRESS
        url = reverse('campaign-change-status', args=[camp.pk])
        r = self.player_client.post(url, {'status': Campaign.STATUS_PENDING})
        assert r.status_code == 404
        r = self.gm_client.post(url, {'status': Campaign.STATUS_PENDING})
        self.assertRedirects(r, camp.get_absolute_url())
        assert Campaign.objects.get().status == Campaign.STATUS_PENDING
        r = self.gm_client.post(url, {'status': 'Foo'})
        assert r.status_code == 400


class CampJoinTestCase(TestCase):
    def setUp(self):
        self.campaign = CampaignFactory()
        self.url = reverse_lazy('campaign-join', args=[self.campaign.pk])
        self.client = AuthenticatedClient(is_gm=False)

    def test_join_game(self):
        r = self.client.post(self.url)
        self.assertRedirects(r, self.campaign.get_absolute_url())

    def test_join_unavailable_game(self):
        self.campaign.accepting_players = False
        self.campaign.save()
        r = self.client.post(self.url)
        assert r.status_code == 404

    def test_join_full_game(self):
        self.campaign.players.add(UserFactory())
        self.campaign.max_players = 1
        self.campaign.save()
        r = self.client.post(self.url)
        assert r.status_code == 404

    def test_join_game_already_on(self):
        self.campaign.players.add(self.client.user)
        r = self.client.post(self.url)
        assert r.status_code == 403
