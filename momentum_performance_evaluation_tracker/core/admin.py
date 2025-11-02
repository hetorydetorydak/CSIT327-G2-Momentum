from django.contrib import admin
from django.contrib.sessions.models import Session
from django.utils import timezone
from .models import Role, Employee, UserAccount

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


# UserAccount Admin
class UserAccountAdmin(admin.ModelAdmin):
    list_display = ['username', 'get_employee_name', 'get_employee_email', 'role', 'is_first_login', 'last_login']
    list_filter = ['role', 'is_first_login', 'last_login']
    search_fields = ['username', 'employee__first_name', 'employee__last_name']
   
    def get_employee_name(self, obj):
        return f"{obj.employee.first_name} {obj.employee.last_name}"
    get_employee_name.short_description = 'Employee Name'
   
    def get_employee_email(self, obj):
        return obj.employee.email_address
    get_employee_email.short_description = 'Email'


# Register your models here
admin.site.register(Role, RoleAdmin)
admin.site.register(Employee, EmployeeAdmin)
admin.site.register(UserAccount, UserAccountAdmin)
