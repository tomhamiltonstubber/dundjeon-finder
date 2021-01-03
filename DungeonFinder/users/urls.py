from django.contrib.auth.views import LogoutView
from django.urls import path

from DungeonFinder.users import views

urlpatterns = [
    path('login/', views.login, name='login'),
    path('logout/', LogoutView.as_view(template_name='base.jinja'), name='logout'),
    path('profile/', views.user_profile, name='profile'),
    path('profile/edit/', views.edit_profile, name='profile-edit'),
    path('player/<str:screen_name>/', views.player_profile, name='player-profile'),
    path('gm/<str:screen_name>/', views.gm_profile, name='gm-profile'),
    path('signup/', views.user_signup, name='signup'),
    path('signup/pending/', views.signup_pending, name='signup-pending'),
    path('signup/confirm/<str:key>/', views.signup_confirm, name='signup-confirm'),
    path('themes/', views.user_update_theme, name='user-themes'),
]
