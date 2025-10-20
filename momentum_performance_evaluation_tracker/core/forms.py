from django import forms
from .models import UserAccount

class SupervisorPasswordResetForm(forms.Form):
    current_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Enter your current password',
            'required': 'required'
        }),
        label="Current Password"
    )
    new_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Enter new password',
            'required': 'required'
        }),
        label="New Password",
        min_length=8
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Confirm new password',
            'required': 'required'
        }),
        label="Confirm New Password"
    )

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        current_password = cleaned_data.get('current_password')
        new_password = cleaned_data.get('new_password')
        confirm_password = cleaned_data.get('confirm_password')

        if self.user and not self.user.check_password(current_password):
            raise forms.ValidationError("Current password is incorrect")

        if new_password and confirm_password and new_password != confirm_password:
            raise forms.ValidationError("New passwords do not match")

        return cleaned_data

