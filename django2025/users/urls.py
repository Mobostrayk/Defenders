
from django.contrib import admin
from django.urls import path

from . import views

urlpatterns = [
    path('login/', views.user_login, name='login'),
    path('registration/', views.registration, name='registration'),
    path('verify-email/<str:email>/', views.verify_email, name='verify_email'),
    path('profile/', views.profile, name='profile'),
    path('logout/', views.logout, name='logout'),
    path('password_reset/', views.logout, name='password_reset'),
    path('check_username/', views.check_username, name='check_username'),
    path('check_email/', views.check_email, name='check_email'),
    path('resend-code/', views.resend_code, name='resend_code'),

    path('track-habits/', views.track_habits, name='track_habits'),
    path('update-habit-completion/', views.update_habit_completion, name='update_habit_completion'),
    path('habit-settings/<int:habit_id>/', views.habit_settings, name='habit_settings'),
    path('habit-stats/<int:habit_id>/', views.habit_stats, name='habit_stats'),
]
