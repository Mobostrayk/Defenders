
from django.contrib import admin
from django.urls import path

from . import views

urlpatterns = [
    path('login/', views.user_login, name='login'),
    path('registration/', views.registration, name='registration'),
    path('profile/', views.profile, name='profile'),
    path('logout/', views.logout, name='logout'),
    path('password_reset/', views.logout, name='password_reset'),

]