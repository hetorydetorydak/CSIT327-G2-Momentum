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