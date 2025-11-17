from django.contrib import admin
from django.contrib.sessions.models import Session
from django.utils import timezone
from django.contrib.auth.hashers import make_password
from django import forms
from .models import Role, Employee, UserAccount

# Session
class SessionAdmin(admin.ModelAdmin):
    list_display = ['session_key', 'get_user', 'session_created', 'session_expires', 'is_expired']
    list_filter = ['expire_date']
    search_fields = ['session_data']
    readonly_fields = ['session_key', 'session_data_decoded', 'session_created', 'session_expires']
   
    def get_user(self, obj):
        session_data = obj.get_decoded()
        user_id = session_data.get('_auth_user_id')
        if user_id:
            try:
                user = UserAccount.objects.get(id=user_id)
                return f"{user.username} ({user.employee.first_name} {user.employee.last_name})"
            except UserAccount.DoesNotExist:
                return "User not found"
        return "No user"
    get_user.short_description = 'User'
   
    def session_created(self, obj):
        # calc when the session was created (8 hours from expire_date)
        created_time = obj.expire_date - timezone.timedelta(seconds=28800)
        # convert to ph time for display
        return timezone.localtime(created_time)
    session_created.short_description = 'Session Created (PH Time)'
   
    def session_expires(self, obj):
        # show expiration time in ph time
        return timezone.localtime(obj.expire_date)
    session_expires.short_description = 'Session Expires (PH Time)'
   
    def is_expired(self, obj):
        return obj.expire_date < timezone.now()
    is_expired.short_description = 'Expired?'
    is_expired.boolean = True
   
    def session_data_decoded(self, obj):
        return obj.get_decoded()
    session_data_decoded.short_description = 'Session Data (Decoded)'

# Role Admin
class RoleAdmin(admin.ModelAdmin):
    list_display = ['role_id', 'role_name', 'description']
    search_fields = ['role_name']
    list_filter = ['role_id']


# Employee Admin  
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name', 'email_address', 'department', 'position', 'hire_date']
    search_fields = ['first_name', 'last_name', 'email_address']
    list_filter = ['department', 'position', 'hire_date']

class UserAccountAdminForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(render_value=True),
        required=False,
        help_text="Leave empty to keep current password, or enter a new password."
    )

    class Meta:
        model = UserAccount
        fields = '__all__'

class UserAccountAdmin(admin.ModelAdmin):
    form = UserAccountAdminForm
    list_display = ['username', 'get_employee_name', 'get_employee_email', 'role', 'is_first_login', 'last_login']
    list_filter = ['role', 'is_first_login', 'last_login']
    search_fields = ['username', 'employee__first_name', 'employee__last_name']
   
    def get_employee_name(self, obj):
        return f"{obj.employee.first_name} {obj.employee.last_name}"
    get_employee_name.short_description = 'Employee Name'
   
    def get_employee_email(self, obj):
        return obj.employee.email_address
    get_employee_email.short_description = 'Email'

    def save_model(self, request, obj, form, change):
        if form.cleaned_data.get('password'):
            obj.password = make_password(form.cleaned_data['password'])
        super().save_model(request, obj, form, change)

admin.site.register(Role, RoleAdmin)
admin.site.register(Employee, EmployeeAdmin)
admin.site.register(UserAccount, UserAccountAdmin)
admin.site.register(Session, SessionAdmin)