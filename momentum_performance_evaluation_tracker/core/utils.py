from django.utils import timezone
from datetime import timedelta
from .models import AttendanceRecord, BacklogItem, EvaluationKPI, KPI, Employee

def calculate_attendance_rate(employee, period=None):
    """Calculate attendance rate for an employee"""
    try:
        today = timezone.now().date()
        start_date = today.replace(day=1) # start of the month
        
        attendance_records = AttendanceRecord.objects.filter(
            employee=employee,
            date__gte=start_date,
            date__lte=today
        )
        
        if not attendance_records.exists():
            return 0.0
        
        total_days = attendance_records.count()
        present_days = attendance_records.filter(status='Present').count()
        
        return round((present_days / total_days) * 100, 2) if total_days > 0 else 0.0
    except Exception as e:
        print(f"Error calculating attendance: {e}")
        return 0.0

def calculate_backlog_count(employee):
    """Count pending backlog items for an employee"""
    try:
        return BacklogItem.objects.filter(
            employee=employee, 
            status='Pending'
        ).count()
    except Exception as e:
        print(f"Error calculating backlog: {e}")
        return 0

def calculate_compliance_rate(employee, period=None):
    """calculate compliance rate based on KPI evaluations"""
    try:
        # latest evaluation for this employee
        latest_evaluation = employee.evaluations.order_by('-evaluation_date').first()
        
        if not latest_evaluation:
            return 0.0
        
        kpi_scores = EvaluationKPI.objects.filter(evaluation=latest_evaluation)
        
        if not kpi_scores.exists():
            return 0.0
        
        total_percentage = 0
        kpi_count = 0
        
        for kpi_score in kpi_scores:
            # calc percentage for each KPI (capped at 100%)
            kpi_percentage = min((kpi_score.value / kpi_score.target) * 100, 100)
            total_percentage += kpi_percentage
            kpi_count += 1
        
        # return average of all KPI percentages
        return round(total_percentage / kpi_count, 2) if kpi_count > 0 else 0.0
        
    except Exception as e:
        print(f"Error calculating compliance: {e}")
        return 0.0

def get_team_kpis(manager_user):
    """Get KPI data for manager's team"""
    try:
        from dashboard.models import TeamMember
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
            total_compliance += calculate_compliance_rate(employee)
            total_attendance += calculate_attendance_rate(employee)
            total_backlogs += calculate_backlog_count(employee)
        
        return {
            'total_employees': total_employees,
            'avg_compliance': round(total_compliance / total_employees, 2),
            'avg_attendance': round(total_attendance / total_employees, 2),
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

def calculate_performance_score(employee):
    """Calculate overall performance score for an employee"""
    try:
        attendance_rate = calculate_attendance_rate(employee)
        backlog_count = calculate_backlog_count(employee)
        compliance_rate = calculate_compliance_rate(employee)
        
        # Simple weighted average calculation
        performance_score = (
            (attendance_rate * 0.4) + 
            ((100 - min(backlog_count * 10, 100)) * 0.3) + 
            (compliance_rate * 0.3)
        )
        
        return round(performance_score, 2)
    except Exception as e:
        print(f"Error calculating performance score: {e}")
        return 0.0

def get_employee_status(employee):
    """Determine employee performance status"""
    score = calculate_performance_score(employee)
    if score >= 85:
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
        from dashboard.models import TeamMember
    
        team_members = TeamMember.objects.filter(
            manager=manager_user, 
            is_active=True
        ).select_related('employee')
        
        team_performance = []
        
        for team_member in team_members:
            employee = team_member.employee
            
            attendance_rate = calculate_attendance_rate(employee)
            backlog_count = calculate_backlog_count(employee)
            compliance_rate = calculate_compliance_rate(employee)
            
            performance_score = round((attendance_rate + compliance_rate) / 2, 2)
            
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
        
        print(f"DEBUG: Found {len(team_performance)} team members for {manager_user.username}")
        return team_performance
        
    except Exception as e:
        print(f"Error getting team performance data: {e}")
        return []