from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.home_page, name='home'),
    path('login/', views.login_page, name='login'),
    path('registration/', views.registration, name='registration'),
    path('check_email/', views.check_email_exists, name='check_email'),
    path('check_username/', views.check_username_exists, name='check_username'),
    path('logout/', views.logout_view, name='logout'),
    path('handle-password-reset/', views.handle_password_reset, name='handle_password_reset'),
    path('admin/create-supervisor/', views.admin_create_supervisor, name='admin_create_supervisor'),
    path('admin/create-admin/', views.admin_create_admin, name='admin_create_admin'),
    path('admin/get-admins/', views.get_admins_api, name='get_admins_api'),
    path('admin/get-supervisors/', views.get_supervisors_api, name='get_supervisors_api'),
    path('admin/get-employees/', views.get_employees_api, name='get_employees_api'),
    path('admin/get-all-users/', views.get_all_users_api, name='get_all_users_api'),
]