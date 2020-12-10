from django import forms

from DungeonFinder.common.forms import DFForm, date2datetime
from DungeonFinder.games.models import Campaign


class CampaignsFilterForm(DFForm):
    campaign_type = forms.ChoiceField(choices=((None, 'All'), *Campaign.TYPE_CHOICES), required=False)
    beginners_welcome = forms.BooleanField(required=False)
    next_game_from = forms.DateField(required=False, widget=forms.HiddenInput)
    next_game_to = forms.DateField(required=False, widget=forms.HiddenInput)
    role_play_level = forms.ChoiceField(choices=Campaign.RP_CHOICES, required=False)
    price_per_session_from = forms.IntegerField(required=False, widget=forms.HiddenInput)
    price_per_session_to = forms.IntegerField(required=False, widget=forms.HiddenInput)
    exclude_mature_content = forms.BooleanField(required=False)

    def clean_next_game_from(self):
        if dt_from := self.cleaned_data.get('next_game_from'):
            return date2datetime(dt_from)

    def clean_next_game_to(self):
        if dt_to := self.cleaned_data.get('next_game_to'):
            return date2datetime(dt_to)
