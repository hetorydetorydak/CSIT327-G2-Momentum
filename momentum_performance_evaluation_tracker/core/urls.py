from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.home_page, name='home'),
    path('login/', views.login_page, name='login'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('registration/', views.registration, name='registration'),
    path('check_email/', views.check_email_exists, name='check_email'),
    path('check_username/', views.check_username_exists, name='check_username'),
]