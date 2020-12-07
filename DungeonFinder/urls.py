from django.contrib import admin
from django.urls import path

from DungeonFinder.games.views import index, games_list

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', index, name='dashboard'),
    path('games/', games_list, name='games-list'),
]
