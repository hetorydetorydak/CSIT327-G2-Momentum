from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from core.forms import SupervisorPasswordResetForm
from core.utils import calculate_attendance_rate, calculate_backlog_count, calculate_compliance_rate, get_team_kpis
from django.http import JsonResponse
from core.models import Employee, Evaluation, BacklogItem, AttendanceRecord
from core.utils import calculate_attendance_rate, calculate_backlog_count, calculate_compliance_rate


@never_cache
@login_required(login_url='/login/')
def dashboard_home(request):
    if not request.user.is_authenticated:
        return redirect('core:login')

    user_is_manager = False
    show_password_reset = False
    password_reset_form = None
    kpi_data = {}

    # Check if user is a manager
    if hasattr(request.user, 'role') and request.user.role.role_id == 302:
        user_is_manager = True

    # Check if supervisor needs password reset
    if hasattr(request.user, 'role') and user_is_manager and request.user.is_first_login:
        show_password_reset = True
        password_reset_form = SupervisorPasswordResetForm(user=request.user)
    
    # Get KPI data based on user role
    if user_is_manager:
        # Manager dashboard - team KPIs
        kpi_data = get_team_kpis(request.user)
    else:
        # Employee dashboard - individual KPIs
        employee = request.user.employee
        kpi_data = {
            'attendance_rate': calculate_attendance_rate(employee),
            'backlog_count': calculate_backlog_count(employee),
            'compliance_rate': calculate_compliance_rate(employee),
        }
    
    context = {
        'user_account': request.user,
        'employee': request.user.employee,
        'show_password_reset': show_password_reset,
        'password_reset_form': password_reset_form,
        'user_is_manager': user_is_manager,
        'kpi_data': kpi_data,  # Add KPI data to context
    }
    return render(request, "dashboard/dashboard.html", context)

@login_required
def employee_performance_api(request, employee_id):
    """API endpoint for drill-down employee performance data"""
    try:
        if request.user.role.role_id != 302:  # Only managers can access
            return JsonResponse({'error': 'Unauthorized'}, status=403)
        
        employee = Employee.objects.get(id=employee_id)
        
        # Get detailed performance data
        performance_data = {
            'employee_name': f"{employee.first_name} {employee.last_name}",
            'position': employee.position,
            'department': employee.department,
            'attendance_rate': calculate_attendance_rate(employee),
            'backlog_count': calculate_backlog_count(employee),
            'compliance_rate': calculate_compliance_rate(employee),
            'recent_evaluations': [],
            'pending_tasks': [],
            'attendance_history': []
        }
        
        # Get recent evaluations
        recent_evaluations = Evaluation.objects.filter(
            employee=employee
        ).order_by('-evaluation_date')[:5]
        
        for evaluation in recent_evaluations:
            performance_data['recent_evaluations'].append({
                'period': evaluation.period,
                'date': evaluation.evaluation_date.strftime('%Y-%m-%d'),
                'kpi_scores': [
                    {
                        'kpi_name': ekpi.kpi.name,
                        'score': ekpi.value,
                        'target': ekpi.target
                    }
                    for ekpi in evaluation.kpi_scores.all()
                ]
            })
        
        # Get pending tasks
        pending_tasks = BacklogItem.objects.filter(
            employee=employee, 
            status='Pending'
        ).order_by('due_date')[:10]
        
        for task in pending_tasks:
            performance_data['pending_tasks'].append({
                'description': task.task_description,
                'due_date': task.due_date.strftime('%Y-%m-%d'),
                'priority': task.priority
            })
        
        # Get recent attendance
        recent_attendance = AttendanceRecord.objects.filter(
            employee=employee
        ).order_by('-date')[:10]
        
        for attendance in recent_attendance:
            performance_data['attendance_history'].append({
                'date': attendance.date.strftime('%Y-%m-%d'),
                'status': attendance.status
            })
        
        return JsonResponse(performance_data)
        
    except Employee.DoesNotExist:
        return JsonResponse({'error': 'Employee not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
def team_kpi_api(request):
    """API endpoint for team KPI data"""
    try:
        if request.user.role.role_id != 302:  # Only managers can access
            return JsonResponse({'error': 'Unauthorized'}, status=403)
        
        team_data = get_team_kpis(request.user)
        return JsonResponse(team_data)
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)