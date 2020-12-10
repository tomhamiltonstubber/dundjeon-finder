from django.contrib import admin
from django.contrib.auth.views import LogoutView
from django.urls import include, path

from DungeonFinder.games.views import index
from DungeonFinder.users.views import login

urlpatterns = [
    path('', index, name='dashboard'),
    path('admin/', admin.site.urls),
    path('login/', login, name='login'),
    path('logout/', LogoutView.as_view(template_name='base.jinja'), name='logout'),
    path('', include('DungeonFinder.games.urls')),
]
