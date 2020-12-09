from django.contrib import admin
from django.contrib.auth.views import LogoutView
from django.urls import path

from DungeonFinder.games.views import available_campaigns_list, campaign_available_list_data, campaign_details, index
from DungeonFinder.users.views import login

urlpatterns = [
    path('', index, name='dashboard'),
    path('admin/', admin.site.urls),
    path('login/', login, name='login'),
    path('logout/', LogoutView.as_view(template_name='base.jinja'), name='logout'),
    path('campaigns/', available_campaigns_list, name='avail-campaign-list'),
    path('campaigns/<int:pk>/', campaign_details, name='campaign-details'),
    path('campaigns/data/', campaign_available_list_data, name='avail-campaigns-data'),
]
