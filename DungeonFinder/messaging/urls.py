from django.urls import path

from DungeonFinder.messaging import views

urlpatterns = [
    path('campaign/<int:pk>/data/', views.message_feed, name='camp-message-feed'),
    path('campaign/<int:pk>/add/', views.create_message, name='camp-message-add'),
    path('<int:pk>/edit/', views.edit_message, name='message-edit'),
    path('<int:pk>/delete/', views.delete_message, name='message-delete'),
]
