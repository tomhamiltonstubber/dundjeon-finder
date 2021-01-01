from django.contrib import admin
from django.urls import include, path

from DungeonFinder.common.views import handle_404, index, blog, blog_detail

handler404 = handle_404

urlpatterns = [
    path('', index, name='dashboard'),
    path('blog', blog, name='blog_list'),
    path('blog-detail', blog_detail, name='blog_detail'),
    path('admin/', admin.site.urls),
    path('', include('DungeonFinder.users.urls')),
    path('', include('DungeonFinder.games.urls')),
    path('', include('DungeonFinder.messaging.urls')),
]
