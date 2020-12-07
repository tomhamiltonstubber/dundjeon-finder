from django.shortcuts import render
from django.views.generic import ListView

from DungeonFinder.games.models import Game


def index(request):
    return render(request, 'index.jinja')


class GamesList(ListView):
    model = Game
    template_name = 'games/list.jinja'
    context_object_name = 'games'


games_list = GamesList.as_view()
