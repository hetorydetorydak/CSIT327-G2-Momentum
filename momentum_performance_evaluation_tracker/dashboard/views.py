from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from core.forms import SupervisorPasswordResetForm
from core.utils import calculate_attendance_rate, calculate_backlog_count, calculate_compliance_rate, get_team_kpis
from django.http import JsonResponse
from core.models import Employee, Evaluation, BacklogItem, AttendanceRecord
from core.utils import calculate_attendance_rate, calculate_backlog_count, calculate_compliance_rate, get_team_performance_data, calculate_performance_score
from .models import TeamMember
from django.db.models import Q 
from core.models import BacklogItem
from django.utils import timezone
from datetime import datetime
from django.shortcuts import get_object_or_404
from dashboard.forms import TaskFileForm
import json

@never_cache
@login_required(login_url='/login/')
def dashboard_home(request):
    if not request.user.is_authenticated:
        return redirect('core:login')

    user_is_manager = False
    user_is_admin = False
    show_password_reset = False
    password_reset_form = None
    kpi_data = {}
    team_performance = []
    
    # Check if user is a manager
    if hasattr(request.user, 'role') and request.user.role.role_id == 302:
        user_is_manager = True
        team_performance = get_team_performance_data(request.user)
        
        # Get filter parameters from request
        department_filter = request.GET.get('department', '')
        status_filter = request.GET.get('status', '')
        
        # Apply filters if provided
        if department_filter or status_filter:
            from core.utils import filter_team_performance
            team_performance = filter_team_performance(team_performance, department_filter, status_filter)

    # Check if user is an admin (role_id = 301)
    if hasattr(request.user, 'role') and request.user.role.role_id == 301:
        user_is_admin = True
    
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
        'user_is_admin': user_is_admin,
        'kpi_data': kpi_data,
        'team_performance': team_performance,
        'selected_department': request.GET.get('department', ''),
        'selected_status': request.GET.get('status', ''),
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
            'performance_score': calculate_performance_score(employee),
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
                'date': evaluation.evaluation_date,
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
                'due_date': task.due_date,
                'priority': task.priority
            })
        
        # Get recent attendance
        recent_attendance = AttendanceRecord.objects.filter(
            employee=employee
        ).order_by('-date')[:10]
        
        for attendance in recent_attendance:
            performance_data['attendance_history'].append({
                'date': attendance.date,
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
                'hire_date': employee.hire_date if employee.hire_date else 'Not specified'
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
                'added_date': member.added_date
            })
        
        return JsonResponse({'team_members': team_data})
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
def get_employee_completed_tasks_api(request, employee_id):
    """API endpoint for supervisor to get completed tasks for a specific employee"""
    try:
        if request.user.role.role_id != 302:
            return JsonResponse({'error': 'Unauthorized'}, status=403)
        
        # Verify employee is in supervisor's team
        from .models import TeamMember
        if not TeamMember.objects.filter(
            manager=request.user,
            employee_id=employee_id,
            is_active=True
        ).exists():
            return JsonResponse({'error': 'Unauthorized'}, status=403)
        
        employee = Employee.objects.get(id=employee_id)
        
        completed_tasks = BacklogItem.objects.filter(
            employee=employee,
            status='Completed',  # Only 'Completed' tasks
            review_status='Pending Review'  # Only tasks pending review
        ).order_by('-completed_date', '-created_date')
        
        tasks_data = []
        for task in completed_tasks:
            tasks_data.append({
                'id': task.backlog_id,
                'description': task.task_description,
                'due_date': task.due_date,
                'completed_date': task.completed_date if task.completed_date else None,
                'priority': task.priority,
                'status': task.status,
                'created_date': task.created_date,
                'has_file': bool(task.task_file),
                'file_name': task.file_name,
                'uploaded_at': task.uploaded_at if task.uploaded_at else None,
                'review_status': task.review_status,
                'reviewed_by': f"{task.reviewed_by.employee.first_name} {task.reviewed_by.employee.last_name}" if task.reviewed_by else None,
                'reviewed_at': task.reviewed_at if task.reviewed_at else None,
                'review_notes': task.review_notes,
                'employee_name': f"{employee.first_name} {employee.last_name}"
            })
        
        return JsonResponse({'tasks': tasks_data})
        
    except Employee.DoesNotExist:
        return JsonResponse({'error': 'Employee not found'}, status=404)
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
            'performance_score': calculate_performance_score(employee),
            'recent_evaluations': [],
            'pending_tasks': [],
            'completed_tasks': [],
            'attendance_history': []
        }
        
        # recent evaluations - PASS DATE OBJECTS
        recent_evaluations = Evaluation.objects.filter(
            employee=employee
        ).order_by('-evaluation_date')[:5]
        
        for evaluation in recent_evaluations:
            performance_data['recent_evaluations'].append({
                'period': evaluation.period,
                'date': evaluation.evaluation_date,  # <-- DATE OBJECT, not string
                'kpi_scores': [
                    {
                        'kpi_name': ekpi.kpi.name,
                        'score': ekpi.value,
                        'target': ekpi.target
                    }
                    for ekpi in evaluation.kpi_scores.all()
                ]
            })
        
        # pending tasks - PASS DATE OBJECTS
        pending_tasks = BacklogItem.objects.filter(
            employee=employee, 
            status__in=['Not Started', 'In Progress']
        ).order_by('due_date')[:10]
        
        for task in pending_tasks:
            performance_data['pending_tasks'].append({
                'id': task.backlog_id,
                'description': task.task_description,
                'due_date': task.due_date,  # <-- DATE OBJECT, not string
                'priority': task.priority,
                'status': task.status,
                'has_file': bool(task.task_file),
                'file_name': task.file_name if task.task_file else None
            })

        # recently completed tasks (for review) - PASS DATE/DATETIME OBJECTS
        completed_tasks = BacklogItem.objects.filter(
            employee=employee,
            status__in=['Completed', 'Accepted']
        ).order_by('-completed_date', '-created_date')[:10]
        
        for task in completed_tasks:
            performance_data['completed_tasks'].append({
                'id': task.backlog_id,
                'description': task.task_description,
                'due_date': task.due_date,  # <-- DATE OBJECT, not string
                'completed_date': task.completed_date if task.completed_date else None,  # <-- DATE OBJECT
                'priority': task.priority,
                'has_file': bool(task.task_file),
                'file_name': task.file_name if task.task_file else None,
                'uploaded_at': task.uploaded_at if task.uploaded_at else None,  # <-- DATETIME OBJECT
                'review_status': task.review_status,
                'reviewed_by': task.reviewed_by.employee.first_name + ' ' + task.reviewed_by.employee.last_name if task.reviewed_by else None,
                'reviewed_at': task.reviewed_at if task.reviewed_at else None,  # <-- DATETIME OBJECT
                'review_notes': task.review_notes
            })
        
        # Get recent attendance - PASS DATE OBJECTS
        recent_attendance = AttendanceRecord.objects.filter(
            employee=employee
        ).order_by('-date')[:10]
        
        for attendance in recent_attendance:
            performance_data['attendance_history'].append({
                'date': attendance.date,  # <-- DATE OBJECT, not string
                'status': attendance.status
            })
        
        # combined template with data
        return render(request, "dashboard/employee_performance_modal.html", {
            'employee_data': performance_data,
            'employee_id': employee_id,
            'user_is_manager': True
        })
        
    except Employee.DoesNotExist:
        return JsonResponse({'error': 'Employee not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
def review_task_api(request, task_id):
    """API endpoint for supervisor to accept or reject a completed task"""
    try:
        if request.method != 'POST':
            return JsonResponse({'error': 'Invalid request method'}, status=400)
        
        if request.user.role.role_id != 302:
            return JsonResponse({'error': 'Unauthorized'}, status=403)
        
        # get the task
        task = BacklogItem.objects.get(backlog_id=task_id)
        
        # verify employee is in supervisor's team
        from .models import TeamMember
        if not TeamMember.objects.filter(
            manager=request.user,
            employee=task.employee,
            is_active=True
        ).exists():
            return JsonResponse({'error': 'Unauthorized'}, status=403)
        
        action = request.POST.get('action')
        review_notes = request.POST.get('review_notes', '')
        
        if action not in ['accept', 'reject']:
            return JsonResponse({'error': 'Invalid action'}, status=400)
        
        if action == 'accept':
            # mark as accepted
            task.review_status = 'Accepted'
            task.status = 'Accepted'
            task.reviewed_by = request.user
            task.reviewed_at = timezone.now()
            task.review_notes = review_notes
            task.save()
            
            return JsonResponse({
                'success': True,
                'message': 'Task accepted successfully!',
                'task': {
                    'id': task.backlog_id,
                    'review_status': task.review_status,
                    'status': task.status,
                    'reviewed_by': f"{request.user.employee.first_name} {request.user.employee.last_name}",
                    'reviewed_at': task.reviewed_at.strftime('%Y-%m-%d %H:%M:%S')
                }
            })
        else:  # reject
            # mark as rejected and change status back to In Progress
            task.review_status = 'Rejected'
            task.status = 'In Progress'  # change back to In Progress
            task.reviewed_by = request.user
            task.reviewed_at = timezone.now()
            task.review_notes = review_notes
            task.completed_date = None  # reset completed date
            task.save()
            
            return JsonResponse({
                'success': True,
                'message': 'Task rejected. It has been returned to In Progress status.',
                'task': {
                    'id': task.backlog_id,
                    'review_status': task.review_status,
                    'status': task.status,
                    'reviewed_by': f"{request.user.employee.first_name} {request.user.employee.last_name}",
                    'reviewed_at': task.reviewed_at.strftime('%Y-%m-%d %H:%M:%S')
                }
            })
        
    except BacklogItem.DoesNotExist:
        return JsonResponse({'error': 'Task not found'}, status=404)
    except Exception as e:
        print("Error in review_task_api:", str(e))
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


@login_required
def get_employee_tasks_api(request):
    """API endpoint for employee to get their assigned tasks"""
    try:
        employee = request.user.employee
        
        tasks = BacklogItem.objects.filter(
            employee=employee
        ).order_by('-created_date', 'priority')
        
        task_data = []
        for task in tasks:
            task_data.append({
                'id': task.backlog_id,
                'description': task.task_description,
                'due_date': task.due_date,
                'status': task.status,
                'priority': task.priority,
                'created_date': task.created_date,
                'completed_date': task.completed_date if task.completed_date else None,
                
                'has_file': bool(task.task_file),
                'file_name': task.file_name,
                'uploaded_at': task.uploaded_at if task.uploaded_at else None,
                
                'review_status': task.review_status,
                'review_notes': task.review_notes if task.review_notes else None,
            })
        
        return JsonResponse({'tasks': task_data})
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
def update_task_status_api(request, task_id):
    """API endpoint for employee to update task status"""
    try:
        if request.method != 'POST':
            return JsonResponse({'error': 'Invalid request method'}, status=400)
            
        employee = request.user.employee
        
        # get the task and verify ownership
        try:
            task = BacklogItem.objects.get(backlog_id=task_id, employee=employee)
        except BacklogItem.DoesNotExist:
            return JsonResponse({'error': 'Task not found or unauthorized'}, status=404)
        
        # check if task is accepted - if so, prevent status changes
        if task.review_status == 'Accepted':
            return JsonResponse({'error': 'Cannot change status of accepted tasks'}, status=403)
        
        new_status = request.POST.get('status')
        
        # validate status
        valid_statuses = ['Not Started', 'In Progress', 'Completed', 'Cancelled']
        if new_status not in valid_statuses:
            return JsonResponse({'error': 'Invalid task status'}, status=400)
        
        # update task status
        task.status = new_status
        
        # set completed_date if task is being marked as completed
        if new_status == 'Completed' and not task.completed_date:
            task.completed_date = timezone.now().date()
            task.review_status = 'Pending Review'  # set to pending review when completed
        elif new_status != 'Completed':
            task.completed_date = None
            task.review_status = 'Pending Review'  # reset review status if not completed
            
        task.save()
        
        return JsonResponse({
            'success': True,
            'message': f'Task status updated to {new_status}',
            'task': {
                'id': task.backlog_id,
                'status': task.status,
                'completed_date': task.completed_date if task.completed_date else None,
                'review_status': task.review_status
            }
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def assign_task_api(request):
    """API endpoint for supervisor to assign tasks to employees"""
    try:
        print("DEBUG: assign_task_api called")
        print("DEBUG: User role:", request.user.role.role_id)
        
        if request.user.role.role_id != 302:
            return JsonResponse({'error': 'Unauthorized'}, status=403)
        
        if request.method != 'POST':
            print("DEBUG: Wrong method - got", request.method)
            return JsonResponse({'error': 'Invalid request method'}, status=400)
        
        employee_id = request.POST.get('employee_id')
        task_description = request.POST.get('task_description')
        due_date = request.POST.get('due_date')
        priority = request.POST.get('priority', 'Medium')
        
        print("DEBUG: Form data - employee_id:", employee_id, "description:", task_description, "due_date:", due_date)
        
        # Validate required fields
        if not all([employee_id, task_description, due_date]):
            print("DEBUG: Missing required fields")
            return JsonResponse({'error': 'Missing required fields'}, status=400)
        
        # Verify employee is in supervisor's team
        try:
            team_member = TeamMember.objects.get(
                manager=request.user,
                employee_id=employee_id,
                is_active=True
            )
            employee = team_member.employee
            print("DEBUG: Employee found:", employee.first_name, employee.last_name)
        except TeamMember.DoesNotExist:
            print("DEBUG: Employee not in team")
            return JsonResponse({'error': 'Employee not found in your team'}, status=403)
        
        # Create the task with 'Not Started' status
        task = BacklogItem.objects.create(
            employee=employee,
            task_description=task_description,
            due_date=due_date,
            priority=priority,
            status='Not Started'
        )
        
        
        # Format the due_date for response
        if isinstance(task.due_date, str):
            due_date_obj = datetime.strptime(task.due_date, '%Y-%m-%d')
            due_date_str = due_date_obj
        else:
            due_date_str = task.due_date
        
        return JsonResponse({
            'success': True,
            'message': f'Task assigned to {employee.first_name} {employee.last_name}',
            'task': {
                'id': task.backlog_id,
                'description': task.task_description,
                'due_date': due_date_str,
                'priority': task.priority,
                'status': task.status
            }
        })
        
    except Exception as e:
        print("DEBUG: Error in assign_task_api:", str(e))
        return JsonResponse({'error': str(e)}, status=500)

@login_required
def upload_task_file_api(request, task_id):
    """API endpoint for employee to upload file for a task"""
    try:
        if request.method != 'POST':
            return JsonResponse({'error': 'Invalid request method'}, status=400)
            
        employee = request.user.employee
        
        # Get the task and verify ownership
        try:
            task = BacklogItem.objects.get(backlog_id=task_id, employee=employee)
        except BacklogItem.DoesNotExist:
            return JsonResponse({'error': 'Task not found or unauthorized'}, status=404)

        # check if task is accepted - if so, prevent file removal
        if task.review_status == 'Accepted':
            return JsonResponse({'error': 'Cannot modify files for accepted tasks'}, status=403)

        if request.content_type == "application/json":
            body = json.loads(request.body)
            if body.get("remove_file"):
                # Delete from Cloudinary if exists
                if task.task_file:
                    try:
                        cloudinary.uploader.destroy(task.task_file.public_id)
                    except Exception as e:
                        print("Error deleting Cloudinary file:", e)

                # Reset database fields
                task.task_file = None
                task.file_name = None
                task.uploaded_at = None
                task.save()

                return JsonResponse({'success': True, 'message': 'File removed successfully'})
        
        form = TaskFileForm(request.POST, request.FILES, instance=task)
        
        if form.is_valid():
            task = form.save(commit=False)
            if task.task_file:
                task.file_name = task.task_file.name
                task.uploaded_at = timezone.now()
            task.save()
            
            return JsonResponse({
                'success': True,
                'message': 'File uploaded successfully!',
                'file_info': {
                    'file_name': task.file_name,
                    'uploaded_at': task.uploaded_at.strftime('%Y-%m-%d %H:%M:%S') if task.uploaded_at else None,
                    'file_url': task.task_file.url if task.task_file else None
                }
            })
        else:
            return JsonResponse({'error': 'Invalid file upload'}, status=400)
            
    except Exception as e:
        print("Error in upload_task_file_api:", str(e))
        return JsonResponse({'error': str(e)}, status=500)

@login_required
def get_task_file_info_api(request, task_id):
    """API endpoint to get file info for a task"""
    try:
        # For employees: can only see their own tasks
        # For managers: can see tasks of employees in their team
        if request.user.role.role_id == 303:  # Employee
            task = BacklogItem.objects.get(backlog_id=task_id, employee=request.user.employee)
        elif request.user.role.role_id == 302:  # Manager
            task = BacklogItem.objects.get(backlog_id=task_id)
            # Verify employee is in manager's team
            from .models import TeamMember
            if not TeamMember.objects.filter(
                manager=request.user,
                employee=task.employee,
                is_active=True
            ).exists():
                return JsonResponse({'error': 'Unauthorized'}, status=403)
        else:
            return JsonResponse({'error': 'Unauthorized'}, status=403)
        
        file_info = {}
        if task.task_file:
            file_info = {
                'has_file': True,
                'file_name': task.file_name,
                'uploaded_at': task.uploaded_at.strftime('%Y-%m-%d %H:%M:%S') if task.uploaded_at else None,
                'file_url': task.task_file.url,
                'task_id': task.backlog_id,
                'employee_name': f"{task.employee.first_name} {task.employee.last_name}"
            }
        else:
            file_info = {
                'has_file': False,
                'task_id': task.backlog_id
            }
        
        return JsonResponse(file_info)
        
    except BacklogItem.DoesNotExist:
        return JsonResponse({'error': 'Task not found'}, status=404)
    except Exception as e:
        print("Error in get_task_file_info_api:", str(e))
        return JsonResponse({'error': str(e)}, status=500)

@login_required
def get_team_tasks_api(request):
    """API endpoint for supervisor to get all team tasks"""
    try:
        if request.user.role.role_id != 302:
            return JsonResponse({'error': 'Unauthorized'}, status=403)
        
        # Get all active team members
        team_members = TeamMember.objects.filter(
            manager=request.user, 
            is_active=True
        ).select_related('employee')
        
        team_tasks = []
        for member in team_members:
            employee = member.employee
            tasks = BacklogItem.objects.filter(employee=employee).order_by('-created_date')
            
            employee_tasks = []
            for task in tasks:
                employee_tasks.append({
                    'id': task.backlog_id,
                    'description': task.task_description,
                    'due_date': task.due_date,
                    'status': task.status,
                    'priority': task.priority,
                    'created_date': task.created_date,
                    
                    'has_file': bool(task.task_file),
                    'file_name': task.file_name,
                    'uploaded_at': task.uploaded_at if task.uploaded_at else None
                })
            
            team_tasks.append({
                'employee_id': employee.id,
                'employee_name': f"{employee.first_name} {employee.last_name}",
                'tasks': employee_tasks
            })
        
        return JsonResponse({'team_tasks': team_tasks})
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)