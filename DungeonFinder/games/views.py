from django.core.exceptions import SuspiciousOperation
from django.db.models import Count, F
from django.http import JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.views.generic import DetailView, ListView

from DungeonFinder.games.forms import GamesFilterForm
from DungeonFinder.games.models import Game


def index(request):
    return render(request, 'index.jinja')


def games_list_data(request):
    form = GamesFilterForm(request=request, data=request.GET)
    form.full_clean()
    if form.is_valid():
        game_qs = Game.objects.annotate(free_spaces=F('max_players') - Count('players'))
        if free_spaces := form.cleaned_data.get('free_spaces'):
            game_qs = game_qs.filter(free_spaces=free_spaces)
        if status := form.cleaned_data.get('status'):
            game_qs = game_qs.filter(status=status)
        data = [
            {
                'name': game.name,
                'link': reverse('game-details', kwargs={'pk': game.pk}),
                'free_spaces': game.free_spaces,
                'description': game.description,
            }
            for game in game_qs
        ]
        return JsonResponse(data, safe=False)
    else:
        raise SuspiciousOperation()


class GamesListView(ListView):
    model = Game
    template_name = 'games/list.jinja'
    context_object_name = 'games'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['filter_form'] = GamesFilterForm(self.request)
        return ctx


games_list = GamesListView.as_view()


class GameDetails(DetailView):
    model = Game
    template_name = 'games/details.jinja'


game_details = GameDetails.as_view()
