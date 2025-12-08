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
    
    path('api/tasks/employee/', views.get_employee_tasks_api, name='employee_tasks'),
    path('api/tasks/<int:task_id>/update-status/', views.update_task_status_api, name='update_task_status'),
    path('api/tasks/assign/', views.assign_task_api, name='assign_task'),
    path('api/tasks/team/', views.get_team_tasks_api, name='team_tasks'),

    path('api/tasks/<int:task_id>/upload-file/', views.upload_task_file_api, name='upload_task_file'),
    path('api/tasks/<int:task_id>/file-info/', views.get_task_file_info_api, name='task_file_info'),
    path('api/employee/<int:employee_id>/completed-tasks/', views.get_employee_completed_tasks_api, name='employee_completed_tasks'),

    path('api/tasks/<int:task_id>/review/', views.review_task_api, name='review_task'),

]