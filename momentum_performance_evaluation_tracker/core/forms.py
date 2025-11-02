from django import forms
from django.contrib.auth import authenticate
from .models import UserAccount, Employee

class LoginForm(forms.Form):
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'placeholder': 'Enter your username',
            'required': 'required'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Enter your password',
            'required': 'required'
        })
    )

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get('username')
        password = cleaned_data.get('password')

        if username and password:
            user = UserAccount.get_by_username(username)
            if not user:
                raise forms.ValidationError("User not found")
            
            if not user.check_password(password):
                raise forms.ValidationError("Invalid password")
            
            cleaned_data['user'] = user
        
        return cleaned_data

class RegistrationForm(forms.Form):
    first_name = forms.CharField(max_length=150)
    last_name = forms.CharField(max_length=150)
    email = forms.EmailField()
    date_hired = forms.DateField(required=False)
    position = forms.CharField(max_length=150, required=False)
    department = forms.CharField(max_length=150, required=False)
    username = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput, min_length=8)
    confirm_password = forms.CharField(widget=forms.PasswordInput)

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and Employee.email_exists(email):
            raise forms.ValidationError("Email address already in use.")
        return email

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if username and UserAccount.username_exists(username):
            raise forms.ValidationError("Username already exists.")
        return username

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError("Passwords do not match!")

        return cleaned_data

    def save(self):
        employee_data = {
            'first_name': self.cleaned_data['first_name'],
            'last_name': self.cleaned_data['last_name'],
            'email_address': self.cleaned_data['email'],
            'hire_date': self.cleaned_data.get('date_hired'),
            'position': self.cleaned_data.get('position'),
            'department': self.cleaned_data.get('department'),
        }
        
        return UserAccount.create_employee_user(
            employee_data=employee_data,
            username=self.cleaned_data['username'],
            password=self.cleaned_data['password']
        )

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