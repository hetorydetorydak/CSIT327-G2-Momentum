from django.db import models
from core.models import Employee, UserAccount

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