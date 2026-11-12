from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('selector/', views.selector, name='selector'),
    path('resorts/', views.resorts, name='resorts'),
    path('profile/', views.profile, name='profile'),
    path('profile/edit/', views.profile_edit, name='profile_edit'),
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='catalog/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('weather/', views.weather_api, name='weather_api'),
    path('favorites/', views.favorites, name='favorites'),
    path('toggle_favorite/<int:snowboard_id>/', views.toggle_favorite, name='toggle_favorite'),
]