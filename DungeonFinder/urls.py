from django.contrib import admin
from django.urls import include, path

from DungeonFinder.common.views import handle_404, index

handler404 = handle_404

urlpatterns = [
    path('', index, name='dashboard'),
    path('admin/', admin.site.urls),
    path('', include('DungeonFinder.users.urls')),
    path('', include('DungeonFinder.games.urls')),
    path('', include('DungeonFinder.messaging.urls')),
]
