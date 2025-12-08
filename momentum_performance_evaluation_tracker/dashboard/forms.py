from django import forms
from core.models import BacklogItem

class TaskFileForm(forms.ModelForm):
    class Meta:
        model = BacklogItem
        fields = ['task_file']
        widgets = {
            'task_file': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf,.doc,.docx,.xls,.xlsx,.jpg,.jpeg,.png,.txt'
            })
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['task_file'].required = False