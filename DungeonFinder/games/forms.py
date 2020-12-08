from django import forms

from DungeonFinder.common.forms import DFForm
from DungeonFinder.games.models import Game


class GamesFilterForm(DFForm):
    free_spaces = forms.IntegerField(min_value=1, required=False)
    status = forms.ChoiceField(choices=Game.STATUS_CHOICES, required=False)
