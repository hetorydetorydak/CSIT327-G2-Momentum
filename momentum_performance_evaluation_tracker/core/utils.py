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

def get_team_kpis(manager):
    """Get team-wide KPI data for manager dashboard"""
    try:
        manager_department = manager.employee.department
        team_employees = Employee.objects.filter(
            department=manager_department,
            accounts__role_id=303
        ).exclude(id=manager.employee.id)
        
        total_employees = team_employees.count()
        total_backlogs = 0
        total_attendance = 0.0
        total_compliance = 0.0
        
        for employee in team_employees:
            total_backlogs += calculate_backlog_count(employee)
            total_attendance += calculate_attendance_rate(employee)
            total_compliance += calculate_compliance_rate(employee)
        
        avg_attendance = round(total_attendance / total_employees, 2) if total_employees > 0 else 0.0
        avg_compliance = round(total_compliance / total_employees, 2) if total_employees > 0 else 0.0
        
        # Calculate how many employees need attention (those with more than 2 backlogs)
        employees_needing_attention_count = 0
        for employee in team_employees:
            if calculate_backlog_count(employee) > 2:
                employees_needing_attention_count += 1
        
        return {
            'total_employees': total_employees,
            'avg_attendance': avg_attendance,
            'avg_compliance': avg_compliance,
            'total_backlogs': total_backlogs,
            'employees_needing_attention': total_backlogs > 15,
            'employees_needing_attention_count': employees_needing_attention_count
        }
    except Exception as e:
        print(f"Error calculating team KPIs: {e}")
        return {
            'total_employees': 0,
            'avg_attendance': 0.0,
            'avg_compliance': 0.0,
            'total_backlogs': 0,
            'employees_needing_attention': False,
            'employees_needing_attention_count': 0
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

def get_team_performance_data(manager):
    """Get detailed performance data for all team members"""
    try:
        manager_department = manager.employee.department
        team_employees = Employee.objects.filter(
            department=manager_department,
            accounts__role_id=303  # Regular employees only
        ).exclude(id=manager.employee.id)
        
        team_performance = []
        for employee in team_employees:
            performance_score = calculate_performance_score(employee)
            
            team_performance.append({
                'employee_id': employee.id,
                'name': f"{employee.first_name} {employee.last_name}",
                'position': employee.position,
                'department': employee.department,
                'performance_score': performance_score,
                'attendance_rate': calculate_attendance_rate(employee),
                'compliance_rate': calculate_compliance_rate(employee),
                'backlog_count': calculate_backlog_count(employee),
                'status': get_employee_status(employee)
            })
        
        # Sort by performance score (highest first)
        team_performance.sort(key=lambda x: x['performance_score'], reverse=True)
        return team_performance
        
    except Exception as e:
        print(f"Error getting team performance data: {e}")
        return []