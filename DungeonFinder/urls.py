from django.contrib import admin
from django.urls import include, path

from DungeonFinder.games.views import index

urlpatterns = [
    path('', index, name='dashboard'),
    path('admin/', admin.site.urls),
    path('', include('DungeonFinder.users.urls')),
    path('', include('DungeonFinder.games.urls')),
]
