from django.core.exceptions import SuspiciousOperation
from django.db.models import Count, F
from django.http import JsonResponse
from django.shortcuts import render
from django.views.generic import DetailView, ListView

from DungeonFinder.games.forms import CampaignsFilterForm
from DungeonFinder.games.models import Campaign


def index(request):
    return render(request, 'index.jinja')


def campaign_available_list_data(request):
    form = CampaignsFilterForm(request=request, data=request.GET)
    form.full_clean()
    if not form.is_valid():
        raise SuspiciousOperation()
    campaign_qs = Campaign.objects.annotate(free_spaces=F('max_players') - Count('players')).filter(
        free_spaces__gt=0, accepting_players=True, status__in={Campaign.STATUS_PENDING, Campaign.STATUS_IN_PROGRESS}
    )
    cd = form.cleaned_data
    if dt_from := cd.get('next_game_from'):
        campaign_qs = campaign_qs.filter(next_game_dt__gte=dt_from)
    if dt_to := cd.get('next_game_to'):
        campaign_qs = campaign_qs.filter(next_game_dt__lt=dt_to)

    if pps_from := cd.get('price_per_session_from'):
        campaign_qs = campaign_qs.filter(price_per_session__gte=pps_from)
    if pps_to := cd.get('price_per_session_to'):
        campaign_qs = campaign_qs.filter(price_per_session__lte=pps_to)

    if camp_type := cd.get('campaign_type'):
        campaign_qs = campaign_qs.filter(campaign_type=camp_type)

    rpl = cd.get('role_play_level')
    if rpl and rpl != Campaign.RP_ANY:
        campaign_qs = campaign_qs.filter(role_play_level=rpl)

    if cd.get('exclude_mature_content'):
        campaign_qs = campaign_qs.exclude(mature_content=True)

    if cd.get('beginners_welcome'):
        campaign_qs = campaign_qs.filter(beginners_welcome=True)

    data = [campaign.get_list_data() for campaign in campaign_qs]
    return JsonResponse(data, safe=False)


class AvailCampaignsListView(ListView):
    model = Campaign
    template_name = 'games/avail-camp-list.jinja'
    context_object_name = 'campaigns'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['filter_form'] = CampaignsFilterForm(self.request)
        return ctx


available_campaigns_list = AvailCampaignsListView.as_view()


class CampaignDetails(DetailView):
    model = Campaign
    template_name = 'games/camp-details.jinja'


campaign_details = CampaignDetails.as_view()
