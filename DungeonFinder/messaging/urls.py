from django.urls import path

from DungeonFinder.messaging import views

url_patterns = [
    path('campaign/<int:pk>/data/', views.message_feed, name='camp-message-feed'),
    path('campaign/<int:pk>/add/', views.create_message, name='camp-message-add'),
    path('<int:pk>/edit/', views.create_message, name='message-edit'),
    path('<int:pk>/delete/', views.create_message, name='message-delete'),
]
