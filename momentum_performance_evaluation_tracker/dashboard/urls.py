from django.urls import path
from . import views

app_name = "dashboard"

urlpatterns = [
    path("", views.dashboard_home, name="home"),
    path("api/employee/<int:employee_id>/performance/", views.employee_performance_api, name="employee_performance_api"),
    path("api/team/kpis/", views.team_kpi_api, name="team_kpi_api"),
]