from django import forms
from core.models import Evaluation, KPI, EvaluationKPI
from django.utils import timezone

class CreateEvaluationForm(forms.ModelForm):
    class Meta:
        model = Evaluation
        fields = ['evaluation_date', 'period', 'notes']
        widgets = {
            'evaluation_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'period': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Q1 2024'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Optional evaluation notes...'}),
        }

class KPIEntryForm(forms.ModelForm):
    kpi = forms.ModelChoiceField(
        queryset=KPI.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control kpi-select'}),
        empty_label="Select KPI"
    )
    
    class Meta:
        model = EvaluationKPI
        fields = ['kpi', 'value', 'target', 'notes']
        widgets = {
            'value': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': 'Actual value'}),
            'target': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': 'Target value', 'value': 100}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'KPI notes (optional)...'}),
        }