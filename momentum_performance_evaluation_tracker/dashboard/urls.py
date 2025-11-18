from django.urls import path
from . import views

app_name = "dashboard"

urlpatterns = [
    path("", views.dashboard_home, name="home"),
    path("api/employee/<int:employee_id>/performance/", views.employee_performance_api, name="employee_performance_api"),
    path("api/team/kpis/", views.team_kpi_api, name="team_kpi_api"),
    path("api/employees/search/", views.search_employees_api, name="search_employees_api"),
    path("api/team/add-employees/", views.add_employees_to_team_api, name="add_employees_to_team"),
    path("api/team/members/", views.get_team_members_api, name="get_team_members"),
    path("modal/employee/<int:employee_id>/performance/", views.employee_performance_modal, name="employee_performance_modal"),
    path("api/team/remove-employee/<int:employee_id>/", views.remove_employee_from_team_api, name="remove_employee_from_team"),
]