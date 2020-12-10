from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import SuspiciousOperation
from django.db.models import Count, F
from django.forms import modelform_factory
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
from django.views.generic import DetailView, ListView

from DungeonFinder.common.forms import DFModelForm
from DungeonFinder.common.views import DFCreateView, DFEditView
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

    def get_context_data(self, **kwargs):
        camp = self.get_object()
        game_details_visible = self.request.user.is_authenticated and (
            self.request.user.id in self.get_object().players.values_list('id', flat=True)
            or (self.request.user.gamemaster and camp.creator_id == self.request.user.gamemaster.id)
        )
        return super().get_context_data(game_details_visible=game_details_visible, **kwargs)


campaign_details = CampaignDetails.as_view()


class CampaignUpdateMixin(LoginRequiredMixin):
    model = Campaign
    template_name = 'games/camp-edit.jinja'


class CampaignCreate(CampaignUpdateMixin, DFCreateView):
    form_class = modelform_factory(model=Campaign, form=DFModelForm, fields='__all__')

    def dispatch(self, request, *args, **kwargs):
        if not (request.user.is_authenticated and request.user.is_gm):
            messages.info(request, 'Only Game Masters can create games')
            return redirect('avail-campaign-list')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        instance = form.save(commit=False)
        instance.creator = self.request.user.gamemaster
        instance.save()
        return redirect(instance.get_absolute_url())


campaign_create = CampaignCreate.as_view()


class CampaignEdit(CampaignUpdateMixin, DFEditView):
    form_class = modelform_factory(model=Campaign, form=DFModelForm, fields='__all__', exclude=['creator'])

    def get_queryset(self):
        return Campaign.objects.filter(creator=getattr(self.request.user, 'gamemaster', None))


campaign_edit = CampaignEdit.as_view()


@require_POST
@login_required(login_url='/accounts/login/')
def campaign_delete(request, pk):
    obj = get_object_or_404(Campaign.objects.filter(creator=getattr(request.user, 'gamemaster', None)), pk=pk)
    obj.delete()
    return redirect('avail-campaign-list')


@require_POST
@login_required(login_url='/accounts/login/')
def campaign_change_status(request, pk):
    obj = get_object_or_404(Campaign.objects.filter(creator=getattr(request.user, 'gamemaster', None)), pk=pk)
    status = request.POST['status']
    try:
        assert status in [k for k, v in Campaign.STATUS_CHOICES]
    except AssertionError:
        raise SuspiciousOperation('Invalid status chosen')
    obj.status = status
    obj.save()
    return redirect(obj.get_absolute_url())
