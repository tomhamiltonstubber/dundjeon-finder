from django.contrib.auth.views import LogoutView
from django.urls import path

from DungeonFinder.users import views

urlpatterns = [
    path('login/', views.login, name='login'),
    path('logout/', LogoutView.as_view(template_name='base.jinja'), name='logout'),
    path('signup/', views.user_signup, name='signup'),
    path('signup/pending/', views.signup_pending, name='signup-pending'),
    path('signup/confirm/<str:key>/', views.signup_confirm, name='signup-confirm'),
]
