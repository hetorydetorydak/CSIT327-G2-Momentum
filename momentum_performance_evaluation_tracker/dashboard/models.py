from django.db import models
from core.models import Employee, UserAccount

class TeamMember(models.Model):
    team_member_id = models.AutoField(primary_key=True)
    manager = models.ForeignKey(UserAccount, on_delete=models.CASCADE, related_name='managed_team')
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='team_memberships')
    added_date = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        unique_together = ['manager', 'employee']
        verbose_name = 'Team Member'
        verbose_name_plural = 'Team Members'
    
    def __str__(self):
        return f"{self.manager.employee} -> {self.employee}"

class Report(models.Model):
    report_id = models.AutoField(primary_key=True)
    generated_by = models.ForeignKey(UserAccount, on_delete=models.CASCADE)
    report_date = models.DateField(auto_now_add=True)
    title = models.CharField(max_length=255)

    def __str__(self):
        return self.title

class PerformanceSnapshot(models.Model):
    snapshot_id = models.AutoField(primary_key=True)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    period = models.CharField(max_length=50)
    summary_score = models.FloatField()

    def __str__(self):
        return f"Snapshot {self.snapshot_id}"