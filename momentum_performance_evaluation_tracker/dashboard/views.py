from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from core.forms import SupervisorPasswordResetForm
from core.utils import calculate_attendance_rate, calculate_backlog_count, calculate_compliance_rate, get_team_kpis
from django.http import JsonResponse
from core.models import Employee, Evaluation, BacklogItem, AttendanceRecord
from core.utils import calculate_attendance_rate, calculate_backlog_count, calculate_compliance_rate, get_team_performance_data
from .models import TeamMember
from django.db.models import Q 

@never_cache
@login_required(login_url='/login/')
def dashboard_home(request):
    if not request.user.is_authenticated:
        return redirect('core:login')

    user_is_manager = False
    show_password_reset = False
    password_reset_form = None
    kpi_data = {}
    team_performance = []
    

    # Check if user is a manager
    if hasattr(request.user, 'role') and request.user.role.role_id == 302:
        user_is_manager = True
        team_performance = get_team_performance_data(request.user)

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
        'kpi_data': kpi_data,
        'team_performance': team_performance,
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

@login_required
def search_employees_api(request):
    """API endpoint for searching employees"""
    try:
        if request.user.role.role_id != 302:
            return JsonResponse({'error': 'Unauthorized'}, status=403)
        
        search_query = request.GET.get('q', '').strip()
        
        # fix: only exclude employees who are currently active in any team
        currently_active_team_member_ids = TeamMember.objects.filter(
            is_active=True
        ).values_list('employee_id', flat=True)
        
        employees = Employee.objects.exclude(
            id__in=currently_active_team_member_ids  # only exclude active team members
        ).exclude(
            id=request.user.employee.id  # exclude self
        ).exclude(
            accounts__role__role_id=302  # exclude other managers
        ).distinct()
        
        if search_query:
            employees = employees.filter(
                Q(first_name__icontains=search_query) |
                Q(last_name__icontains=search_query) |
                Q(department__icontains=search_query) |
                Q(position__icontains=search_query) |
                Q(email_address__icontains=search_query)
            )
        
        employees = employees[:50]
        
        employee_data = []
        for employee in employees:
            employee_data.append({
                'id': employee.id,
                'first_name': employee.first_name,
                'last_name': employee.last_name,
                'full_name': f"{employee.first_name} {employee.last_name}",
                'department': employee.department or 'Not specified',
                'position': employee.position or 'Not specified',
                'email': employee.email_address,
                'hire_date': employee.hire_date.strftime('%Y-%m-%d') if employee.hire_date else 'Not specified'
            })
        
        return JsonResponse({'employees': employee_data})
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
def add_employees_to_team_api(request):
    """API endpoint to add employees to manager's team"""
    try:
        if request.user.role.role_id != 302:
            return JsonResponse({'error': 'Unauthorized'}, status=403)
        
        if request.method == 'POST':
            employee_ids = request.POST.getlist('employee_ids[]')
            
            if not employee_ids:
                return JsonResponse({'error': 'No employees selected'}, status=400)
            
            added_employees = []
            failed_employees = []
            
            for employee_id in employee_ids:
                try:
                    employee = Employee.objects.get(id=employee_id)
                    
                    # check if employee is already active in team
                    if TeamMember.objects.filter(manager=request.user, employee=employee, is_active=True).exists():
                        failed_employees.append({
                            'id': employee_id,
                            'name': f"{employee.first_name} {employee.last_name}",
                            'error': 'Already in team'
                        })
                        continue
                    
                    # check if inactive record exists, reactivate it
                    existing_inactive_member = TeamMember.objects.filter(
                        manager=request.user, 
                        employee=employee, 
                        is_active=False
                    ).first()
                    
                    if existing_inactive_member:
                        # reactivate the existing record
                        existing_inactive_member.is_active = True
                        existing_inactive_member.save()
                        team_member = existing_inactive_member
                    else:
                        # create new record
                        team_member = TeamMember.objects.create(
                            manager=request.user,
                            employee=employee
                        )
                    
                    added_employees.append({
                        'id': employee_id,
                        'name': f"{employee.first_name} {employee.last_name}"
                    })
                    
                except Employee.DoesNotExist:
                    failed_employees.append({
                        'id': employee_id,
                        'name': 'Unknown',
                        'error': 'Employee not found'
                    })
                except Exception as e:
                    failed_employees.append({
                        'id': employee_id,
                        'name': f"{employee.first_name} {employee.last_name}" if 'employee' in locals() else 'Unknown',
                        'error': str(e)
                    })
            
            return JsonResponse({
                'success': True,
                'added': added_employees,
                'failed': failed_employees,
                'message': f'Successfully added {len(added_employees)} employees to your team'
            })
        
        return JsonResponse({'error': 'Invalid request method'}, status=400)
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
def get_team_members_api(request):
    """API endpoint to get current team members"""
    try:
        if request.user.role.role_id != 302:
            return JsonResponse({'error': 'Unauthorized'}, status=403)
        
        team_members = TeamMember.objects.filter(
            manager=request.user, 
            is_active=True
        ).select_related('employee')
        
        team_data = []
        for member in team_members:
            employee = member.employee
            team_data.append({
                'id': employee.id,
                'name': f"{employee.first_name} {employee.last_name}",
                'department': employee.department,
                'position': employee.position,
                'email': employee.email_address,
                'added_date': member.added_date.strftime('%Y-%m-%d')
            })
        
        return JsonResponse({'team_members': team_data})
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
def employee_performance_modal(request, employee_id):
    """Render performance modal for a specific employee"""
    try:
        if request.user.role.role_id != 302:
            return JsonResponse({'error': 'Unauthorized'}, status=403)
        
        employee = Employee.objects.get(id=employee_id)
        
        # detailed performance data
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
        
        # recent evaluations
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
        
        # pending tasks
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
        
        # combined template with data
        return render(request, "dashboard/employee_performance_modal.html", {
            'employee_data': performance_data,
            'employee_id': employee_id
        })
        
    except Employee.DoesNotExist:
        return JsonResponse({'error': 'Employee not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
def remove_employee_from_team_api(request, employee_id):
    """API endpoint to remove employee from manager's team using soft deletion"""
    try:
        if request.user.role.role_id != 302:
            return JsonResponse({'error': 'Unauthorized'}, status=403)
        
        if request.method == 'POST':
            employee = Employee.objects.get(id=employee_id)
            
            # find active team member relationship
            team_member = TeamMember.objects.filter(
                manager=request.user,
                employee=employee,
                is_active=True
            ).first()
            
            if not team_member:
                return JsonResponse({
                    'success': False,
                    'error': 'Employee not found in your team'
                }, status=404)
            
            team_member.is_active = False
            team_member.save()
            
            employee_name = f"{employee.first_name} {employee.last_name}"
            
            return JsonResponse({
                'success': True,
                'message': f'{employee_name} has been removed from your team'
            })
        
        return JsonResponse({'error': 'Invalid request method'}, status=400)
        
    except Employee.DoesNotExist:
        return JsonResponse({'error': 'Employee not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)