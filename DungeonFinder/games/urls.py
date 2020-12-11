from django.urls import path

from DungeonFinder.games import views

urlpatterns = [
    path('campaigns/', views.available_campaigns_list, name='avail-campaign-list'),
    path('campaigns/data/', views.campaign_available_list_data, name='avail-campaigns-data'),
    path('campaigns/create/', views.campaign_create, name='campaign-create'),
    path('campaigns/<int:pk>/', views.campaign_details, name='campaign-details'),
    path('campaigns/<int:pk>/edit/', views.campaign_edit, name='campaign-edit'),
    path('campaigns/<int:pk>/change-status/', views.campaign_change_status, name='campaign-change-status'),
    path('campaigns/<int:pk>/delete/', views.campaign_delete, name='campaign-delete'),
    path('campaigns/<int:pk>/join/', views.campaign_join, name='campaign-join'),
]
