from django.contrib import admin
from django.urls import include, path, re_path

from DungeonFinder import settings
from DungeonFinder.common.views import handle_404, index

handler404 = handle_404

urlpatterns = [
    path('', index, name='dashboard'),
    path('admin/', admin.site.urls),
    path('', include('DungeonFinder.users.urls')),
    path('', include('DungeonFinder.games.urls')),
    path('', include('DungeonFinder.messaging.urls')),
]

if not settings.LIVE and (settings.DEBUG or settings.TESTING):  # pragma: no cover
    from django.views.static import serve

    urlpatterns += [
        re_path(
            r'^%s(?P<path>.*)$' % settings.MEDIA_URL.lstrip('/'), serve, kwargs={'document_root': settings.MEDIA_ROOT}
        )
    ]
