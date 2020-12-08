from django.contrib import admin
from django.contrib.auth.views import LogoutView
from django.urls import path

from DungeonFinder.games.views import index, games_list, games_list_data, game_details
from DungeonFinder.users.views import login

urlpatterns = [
    path('', index, name='dashboard'),
    path('admin/', admin.site.urls),
    path('login/', login, name='login'),
    path('logout/', LogoutView.as_view(template_name='base.jinja'), name='logout'),
    path('games/', games_list, name='games-list'),
    path('games/<int:pk>/', game_details, name='game-details'),
    path('games/data/', games_list_data, name='games-data'),
]
