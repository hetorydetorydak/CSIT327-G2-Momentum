from django.utils import timezone
from datetime import timedelta
from .models import AttendanceRecord, BacklogItem, EvaluationKPI, KPI, Employee, Evaluation
from dashboard.models import TeamMember
from django.db.models import Q

def calculate_attendance_rate(employee, period=None):
    """Calculate attendance rate for an employee"""
    try:
        today = timezone.now().date()
        
        # Start from October 1st of the current year
        start_date = today.replace(month=10, day=1)
        
        # If we're in a month before October, use October of previous year
        if today.month < 10:
            start_date = start_date.replace(year=today.year - 1)
        
        attendance_records = AttendanceRecord.objects.filter(
            employee=employee,
            date__gte=start_date,
            date__lte=today
        )
        
        attendance_records = attendance_records.filter(is_counted=False)
        
                
        if not attendance_records.exists():
            return 0.0
        
        total_days = attendance_records.count()
        present_days = attendance_records.filter(status='Present').count()
        
        rate = round((present_days / total_days) * 100, 2) if total_days > 0 else 0.0
        
        return rate
    except Exception as e:
        print(f"Error calculating attendance: {e}")
        return 0.0

def calculate_backlog_count(employee):
    """Count pending backlog items for an employee"""
    try:
        # count tasks that are Not Started, In Progress, or Completed but pending review
        # exclude Accepted tasks
        return BacklogItem.objects.filter(
            employee=employee, 
            status__in=['Not Started', 'In Progress']
        ).exclude(
            review_status='Accepted'  # exclude accepted tasks from backlog count
        ).count()
    except Exception as e:
        print(f"Error calculating backlog: {e}")
        return 0

def calculate_compliance_rate(employee, period_days=None, since_last_evaluation=False, real_time=True):
    """Calculate compliance rate for tasks"""
    try:
        from django.utils import timezone
        from datetime import timedelta
        
        # Base queryset
        tasks = BacklogItem.objects.filter(employee=employee)
        
        # Exclude evaluated tasks in real-time mode
        if real_time:
            # Exclude tasks that were already evaluated
            tasks = tasks.filter(is_evaluated=False)
        
        # Apply date filters if period_days is specified
        if period_days:
            end_date = timezone.now().date()
            start_date = end_date - timedelta(days=period_days)
            tasks = tasks.filter(
                created_date__gte=start_date,
                created_date__lte=end_date
            )
        
        # Filter for tasks since last evaluation if requested
        if since_last_evaluation:
            last_evaluation = Evaluation.objects.filter(
                employee=employee
            ).order_by('-evaluation_date').first()
            
            if last_evaluation:
                tasks = tasks.filter(created_date__gt=last_evaluation.evaluation_date)
        
        if not tasks.exists():
            return 0.0
        
        total_tasks = tasks.count()
        
        # Calculate accepted tasks
        accepted_tasks = tasks.filter(
            Q(status='Accepted') | 
            Q(review_status='Accepted')
        ).distinct().count()
        
        # Simple compliance rate calculation
        compliance_rate = (accepted_tasks / total_tasks) * 100 if total_tasks > 0 else 0.0
        
        return round(compliance_rate, 2)
        
    except Exception as e:
        print(f"Error calculating compliance: {e}")
        return 0.0

def calculate_performance_score(employee):
    """Calculate overall performance score for an employee"""
    try:
        attendance_rate = calculate_attendance_rate(employee)
        compliance_rate = calculate_compliance_rate(employee, real_time=True)
        
        # Simple weighted average calculation
        performance_score = (
            (attendance_rate * 0.4) +
            (compliance_rate * 0.6)
        )
        
        return round(performance_score, 2)
    except Exception as e:
        print(f"Error calculating performance score: {e}")
        return 0.0

def get_employee_status(employee):
    """Determine employee performance status"""
    score = calculate_performance_score(employee)
    if score >= 80:
        return 'excellent'
    elif score >= 70:
        return 'good'
    elif score >= 60:
        return 'needs_improvement'
    else:
        return 'poor'

def get_team_performance_data(manager_user):
    """Get performance data for manager's team members"""
    try:
        team_members = TeamMember.objects.filter(
            manager=manager_user, 
            is_active=True
        ).select_related('employee')
        
        team_performance = []
        
        for team_member in team_members:
            employee = team_member.employee
            
            attendance_rate = calculate_attendance_rate(employee)
            backlog_count = calculate_backlog_count(employee)
            compliance_rate = calculate_compliance_rate(employee, real_time=True)
            performance_score = calculate_performance_score(employee)
            
            if performance_score >= 90:
                status = 'excellent'
            elif performance_score >= 80:
                status = 'good'
            elif performance_score >= 70:
                status = 'needs_improvement'
            else:
                status = 'poor'
            
            team_performance.append({
                'employee_id': employee.id,
                'name': f"{employee.first_name} {employee.last_name}",
                'position': employee.position or 'Not specified',
                'department': employee.department or 'Not specified',
                'performance_score': performance_score,
                'attendance_rate': attendance_rate,
                'compliance_rate': compliance_rate,
                'backlog_count': backlog_count,
                'status': status
            })
        
        return team_performance
        
    except Exception as e:
        print(f"Error getting team performance data: {e}")
        return []

def filter_team_performance(team_performance, department=None, status=None):
    """Filter team performance data by department and/or status"""
    filtered_data = team_performance.copy()
    
    if department:
        filtered_data = [emp for emp in filtered_data if emp.get('department') == department]
    
    if status:
        # map status filter values to status categories
        status_mapping = {
            'Excellent': 'excellent',
            'Good': 'good', 
            'Needs Improvement' : 'needs_improvement',
            'Poor': 'poor'
        }
        
        status_filter = status_mapping.get(status, status.lower())
        
        if isinstance(status_filter, list):
            # if status_filter is a list, check if employee status is in the list
            filtered_data = [emp for emp in filtered_data if emp.get('status') in status_filter]
        else:
            filtered_data = [emp for emp in filtered_data if emp.get('status') == status_filter]

    return filtered_data

def get_employee_compliance_rate(employee, real_time=True):
    """
    Get employee compliance rate.
    """
    try:
        print(f"DEBUG: Getting compliance for {employee} - real_time={real_time}")
        
        if real_time:
            # REAL-TIME calculation - exclude evaluated tasks
            rate = calculate_compliance_rate(employee, real_time=True)
            print(f"DEBUG: Real-time compliance rate = {rate}")
            return rate
        else:
            # Get from latest evaluation
            latest_evaluation = Evaluation.objects.filter(
                employee=employee
            ).order_by('-evaluation_date').first()
            
            if latest_evaluation and latest_evaluation.compliance_rate is not None:
                print(f"DEBUG: Using evaluation compliance rate = {latest_evaluation.compliance_rate}")
                return latest_evaluation.compliance_rate
            else:
                rate = calculate_compliance_rate(employee, real_time=False)
                print(f"DEBUG: Calculated compliance rate = {rate}")
                return rate
    except Exception as e:
        print(f"Error getting compliance rate: {e}")
        return calculate_compliance_rate(employee, real_time=real_time)

def calculate_evaluation_metrics(employee, evaluation_date=None):
    """
    Calculate comprehensive evaluation metrics including attendance
    """
    try:
        # Calculate attendance rate for evaluation period
        attendance_rate = calculate_attendance_rate_for_period(employee, evaluation_date)
        
        # Calculate compliance rate for evaluation period
        compliance_rate = calculate_compliance_rate_for_evaluation(employee, evaluation_date)
        
        # Calculate overall performance with weights
        # You can adjust these weights as needed
        overall_performance = (
            (attendance_rate * 0.4) +  # 40% attendance
            (compliance_rate * 0.6)    # 60% compliance
        )
        
        return {
            'attendance_rate': round(attendance_rate, 2),
            'compliance_rate': round(compliance_rate, 2),
            'overall_performance': round(overall_performance, 2)
        }
        
    except Exception as e:
        print(f"Error calculating evaluation metrics: {e}")
        return {
            'attendance_rate': 0.0,
            'compliance_rate': 0.0,
            'overall_performance': 0.0
        }

def calculate_attendance_rate_for_period(employee, evaluation_date=None):
    """Calculate attendance rate for a specific period"""
    try:
        # Get last evaluation date or default period
        last_evaluation = Evaluation.objects.filter(
            employee=employee
        ).order_by('-evaluation_date').first()
        
        if evaluation_date:
            end_date = evaluation_date
        else:
            end_date = timezone.now().date()
        
        if last_evaluation:
            # Calculate for period since last evaluation
            start_date = last_evaluation.evaluation_date
            attendance_records = AttendanceRecord.objects.filter(
                employee=employee,
                date__gt=start_date,  # After last evaluation
                date__lte=end_date    # Up to current evaluation
            )
        else:
            # First evaluation - use all records
            attendance_records = AttendanceRecord.objects.filter(
                employee=employee,
                date__lte=end_date
            )
        
        if not attendance_records.exists():
            return 0.0
        
        total_days = attendance_records.count()
        present_days = attendance_records.filter(status='Present').count()
        
        rate = (present_days / total_days) * 100 if total_days > 0 else 0.0
        return round(rate, 2)
        
    except Exception as e:
        print(f"Error calculating attendance for period: {e}")
        return 0.0

def calculate_compliance_rate_for_evaluation(employee, evaluation_date=None):
    """Calculate compliance rate for evaluation period"""
    try:
        # Get last evaluation date
        last_evaluation = Evaluation.objects.filter(
            employee=employee
        ).order_by('-evaluation_date').first()
        
        if evaluation_date:
            end_date = evaluation_date
        else:
            end_date = timezone.now().date()
        
        # Get tasks for the evaluation period
        tasks = BacklogItem.objects.filter(employee=employee)
        
        if last_evaluation:
            # Only tasks created after last evaluation
            tasks = tasks.filter(
                created_date__gt=last_evaluation.evaluation_date,
                created_date__lte=end_date
            )
        else:
            # First evaluation - all tasks up to evaluation date
            tasks = tasks.filter(created_date__lte=end_date)
        
        if not tasks.exists():
            return 0.0
        
        total_tasks = tasks.count()
        accepted_tasks = tasks.filter(
            Q(status='Accepted') | 
            Q(review_status='Accepted')
        ).distinct().count()
        
        compliance_rate = (accepted_tasks / total_tasks) * 100 if total_tasks > 0 else 0.0
        return round(compliance_rate, 2)
        
    except Exception as e:
        print(f"Error calculating compliance for evaluation: {e}")
        return 0.0

def reset_rates_after_evaluation(employee):
    """
    Reset rates in dashboard by marking tasks/attendance as 'evaluated'
    This is a conceptual approach - you might need different implementation
    """
    try:
        # Get latest evaluation
        latest_evaluation = Evaluation.objects.filter(
            employee=employee
        ).order_by('-evaluation_date').first()
        
        if not latest_evaluation:
            return False
        
        # Mark tasks created before evaluation as 'evaluated'
        # You might need to add an 'evaluated' field to BacklogItem
        BacklogItem.objects.filter(
            employee=employee,
            created_date__lte=latest_evaluation.evaluation_date
        ).update(is_evaluated=True)  # Assuming you add this field
        
        # Mark attendance before evaluation as 'counted'
        AttendanceRecord.objects.filter(
            employee=employee,
            date__lte=latest_evaluation.evaluation_date
        ).update(is_counted=True)  # Assuming you add this field
        
        return True
        
    except Exception as e:
        print(f"Error resetting rates: {e}")
        return False


def get_team_kpis(manager_user):
    """Get KPI data for manager's team"""
    try:
        team_members = TeamMember.objects.filter(
            manager=manager_user, 
            is_active=True
        ).select_related('employee')
        
        if not team_members.exists():
            return {
                'total_employees': 0,
                'avg_compliance': 0,
                'avg_attendance': 0,
                'total_backlogs': 0
            }
        
        total_employees = team_members.count()
        total_compliance = 0
        total_attendance = 0
        total_backlogs = 0
        
        for team_member in team_members:
            employee = team_member.employee
            total_compliance += get_employee_compliance_rate(employee, real_time=True)  # REAL-TIME
            total_attendance += calculate_attendance_rate(employee)
            total_backlogs += calculate_backlog_count(employee)
        
        return {
            'total_employees': total_employees,
            'avg_compliance': round(total_compliance / total_employees, 2) if total_employees > 0 else 0,
            'avg_attendance': round(total_attendance / total_employees, 2) if total_employees > 0 else 0,
            'total_backlogs': total_backlogs
        }
        
    except Exception as e:
        print(f"Error getting team KPIs: {e}")
        return {
            'total_employees': 0,
            'avg_compliance': 0,
            'avg_attendance': 0,
            'total_backlogs': 0
        }