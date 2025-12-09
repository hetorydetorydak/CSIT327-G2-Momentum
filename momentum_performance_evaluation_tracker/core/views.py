from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth import logout as auth_logout

from .forms import SupervisorPasswordResetForm, LoginForm, RegistrationForm, AdminCreateUserForm
from .models import UserAccount, Employee

from django.contrib.auth.decorators import login_required, user_passes_test
import time

def home_page(request):
    return render(request, "core/home.html")

def login_page(request):
    storage = messages.get_messages(request)
    for message in storage:
        pass

    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            user = form.cleaned_data['user']
            login(request, user, backend='core.backends.CustomUserBackend')
            
            if not (user.role.role_id == 302 and user.is_first_login):
                messages.success(request, f"Welcome back, {user.employee.first_name}!")

            return redirect("dashboard:home")
        else:
            for error in form.errors.values():
                messages.error(request, error)
            
            return render(request, "core/home.html", {"show_login": True, "login_form": form})

    return redirect("core:home")

def registration(request):
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            try:
                user = form.save()
                messages.success(request, "Account created successfully! Please login.")
                return render(request, "core/home.html", {"show_login": True})
            except Exception as e:
                print("Error during registration:", e)
                messages.error(request, "An error occurred during registration. Please try again.")
                return render(request, "core/home.html", {
                    "show_register": True, 
                    "register_form": form,
                    "form_data": request.POST
                })
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
            
            return render(request, "core/home.html", {
                "show_register": True, 
                "register_form": form,
                "form_data": request.POST
            })

    return redirect("core:home")

def logout_view(request):
    request.session.flush()
    
    storage = messages.get_messages(request)
    for message in storage:
        pass

    auth_logout(request)
    return redirect("core:home")

def check_email_exists(request):
    email = request.GET.get("email")
    exists = False
    if email:
        exists = Employee.email_exists(email)
    return JsonResponse({"exists": exists})

def check_username_exists(request):
    username = request.GET.get("username")
    exists = False
    if username:
        exists = UserAccount.username_exists(username)
    return JsonResponse({"exists": exists})

def handle_password_reset(request):
    if not request.user.is_authenticated:
        return redirect('core:login')
    
    if request.method == 'POST':
        form = SupervisorPasswordResetForm(request.POST, user=request.user)
        if form.is_valid():
            new_password = form.cleaned_data['new_password']
            request.user.set_password(new_password)
            request.user.is_first_login = False
            request.user.save()
            
            login(request, request.user, backend='core.backends.CustomUserBackend')
            messages.success(request, "Password updated successfully!")
            return redirect('dashboard:home')
        else:
            for error in form.errors.values():
                messages.error(request, error)

    return redirect('dashboard:home')
    
def is_admin(user):
    """Check if user is admin (role 301)"""
    return user.is_authenticated and hasattr(user, 'role') and user.role.role_id == 301

@login_required
@user_passes_test(is_admin, login_url='/login/')
def admin_create_supervisor(request):
    """Admin creates a new supervisor"""
    if request.method == 'POST':
        form = AdminCreateUserForm(request.POST, user_type='supervisor')
        if form.is_valid():
            try:
                supervisor = form.save()
                return JsonResponse({
                    'success': True,
                    'message': f'Supervisor account created successfully for {supervisor.employee.first_name} {supervisor.employee.last_name}.',
                    'user_id': supervisor.pk,
                    'username': supervisor.username
                })
            except Exception as e:
                return JsonResponse({
                    'success': False,
                    'message': f'Error creating supervisor: {str(e)}'
                })
        else:
            errors = {field: error.get_json_data()[0]['message'] for field, error in form.errors.items()}
            return JsonResponse({
                'success': False,
                'errors': errors,
                'message': 'Please correct the errors below.'
            })
    
    return JsonResponse({'success': False, 'message': 'Invalid request method'})

@login_required
@user_passes_test(is_admin, login_url='/login/')
def admin_create_admin(request):
    """Admin creates another admin (only admins can create admins)"""
    if request.method == 'POST':
        form = AdminCreateUserForm(request.POST, user_type='admin')
        if form.is_valid():
            try:
                admin = form.save()
                return JsonResponse({
                    'success': True,
                    'message': f'Admin account created successfully for {admin.employee.first_name} {admin.employee.last_name}.',
                    'user_id': admin.pk,
                    'username': admin.username
                })
            except Exception as e:
                return JsonResponse({
                    'success': False,
                    'message': f'Error creating admin: {str(e)}'
                })
        else:
            errors = {field: error.get_json_data()[0]['message'] for field, error in form.errors.items()}
            return JsonResponse({
                'success': False,
                'errors': errors,
                'message': 'Please correct the errors below.'
            })
    
    return JsonResponse({'success': False, 'message': 'Invalid request method'})

from django.core.paginator import Paginator
from django.db.models import Q

@login_required
@user_passes_test(is_admin, login_url='/login/')
def get_admins_api(request):
    """API endpoint to get all admin users"""
    try:
        # Get all admin users (role_id = 301)
        admins = UserAccount.objects.filter(
            role__role_id=301
        ).select_related('employee', 'role')
        
        # Convert to list
        admin_data = []
        for admin in admins:
            admin_data.append({
                'id': admin.pk,
                'username': admin.username,
                'employee_name': f"{admin.employee.first_name} {admin.employee.last_name}",
                'email': admin.employee.email_address,
                'role': admin.role.role_name,
                'is_first_login': admin.is_first_login,
                'last_login': admin.last_login.strftime('%Y-%m-%d %H:%M') if admin.last_login else 'Never',
                'position': admin.employee.position or '',
                'department': admin.employee.department or '',
                'hire_date': admin.employee.hire_date.strftime('%Y-%m-%d') if admin.employee.hire_date else ''
            })
        
        return JsonResponse({
            'success': True,
            'admins': admin_data,
            'count': len(admin_data)
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })

@login_required
@user_passes_test(is_admin, login_url='/login/')
def get_supervisors_api(request):
    """API endpoint to get all supervisor users"""
    try:
        # Get all supervisor users (role_id = 302)
        supervisors = UserAccount.objects.filter(
            role__role_id=302
        ).select_related('employee', 'role')
        
        # Convert to list
        supervisor_data = []
        for supervisor in supervisors:
            supervisor_data.append({
                'id': supervisor.pk,
                'username': supervisor.username,
                'employee_name': f"{supervisor.employee.first_name} {supervisor.employee.last_name}",
                'email': supervisor.employee.email_address,
                'role': supervisor.role.role_name,
                'is_first_login': supervisor.is_first_login,
                'last_login': supervisor.last_login.strftime('%Y-%m-%d %H:%M') if supervisor.last_login else 'Never',
                'position': supervisor.employee.position or '',
                'department': supervisor.employee.department or '',
                'hire_date': supervisor.employee.hire_date.strftime('%Y-%m-%d') if supervisor.employee.hire_date else ''
            })
        
        return JsonResponse({
            'success': True,
            'supervisors': supervisor_data,
            'count': len(supervisor_data)
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })

@login_required
@user_passes_test(is_admin, login_url='/login/')
def get_employees_api(request):
    """API endpoint to get all regular employees"""
    try:
        # Get all regular employees (role_id = 303)
        employees = UserAccount.objects.filter(
            role__role_id=303
        ).select_related('employee', 'role')
        
        # Convert to list
        employee_data = []
        for employee in employees:
            employee_data.append({
                'id': employee.pk,
                'username': employee.username,
                'employee_name': f"{employee.employee.first_name} {employee.employee.last_name}",
                'email': employee.employee.email_address,
                'role': employee.role.role_name,
                'is_first_login': employee.is_first_login,
                'last_login': employee.last_login.strftime('%Y-%m-%d %H:%M') if employee.last_login else 'Never',
                'position': employee.employee.position or '',
                'department': employee.employee.department or '',
                'hire_date': employee.employee.hire_date.strftime('%Y-%m-%d') if employee.employee.hire_date else ''
            })
        
        return JsonResponse({
            'success': True,
            'employees': employee_data,
            'count': len(employee_data)
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })

@login_required
@user_passes_test(is_admin, login_url='/login/')
def get_all_users_api(request):
    """API endpoint to get all users with search and pagination"""
    try:
        # Get parameters
        role_filter = request.GET.get('role', 'all')  # 'admin', 'supervisor', 'employee', 'all'
        search_query = request.GET.get('search', '').strip()
        page = int(request.GET.get('page', 1))
        per_page = int(request.GET.get('per_page', 20))
        
        # Base queryset
        users = UserAccount.objects.select_related('employee', 'role')
        
        # Apply role filter
        if role_filter == 'admin':
            users = users.filter(role__role_id=301)
        elif role_filter == 'supervisor':
            users = users.filter(role__role_id=302)
        elif role_filter == 'employee':
            users = users.filter(role__role_id=303)
        
        # Apply search filter
        if search_query:
            users = users.filter(
                Q(username__icontains=search_query) |
                Q(employee__first_name__icontains=search_query) |
                Q(employee__last_name__icontains=search_query) |
                Q(employee__email_address__icontains=search_query) |
                Q(employee__position__icontains=search_query) |
                Q(employee__department__icontains=search_query)
            )
        
        # Get total count
        total_count = users.count()
        
        # Pagination
        paginator = Paginator(users, per_page)
        page_obj = paginator.get_page(page)
        
        # Convert to list
        user_data = []
        for user in page_obj:
            user_data.append({
                'id': user.pk,
                'username': user.username,
                'employee_name': f"{user.employee.first_name} {user.employee.last_name}",
                'email': user.employee.email_address,
                'role_id': user.role.role_id,
                'role': user.role.role_name,
                'is_first_login': user.is_first_login,
                'last_login': user.last_login.strftime('%Y-%m-%d %H:%M') if user.last_login else 'Never',
                'position': user.employee.position or '',
                'department': user.employee.department or '',
                'hire_date': user.employee.hire_date.strftime('%Y-%m-%d') if user.employee.hire_date else ''
            })
        
        return JsonResponse({
            'success': True,
            'users': user_data,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total_pages': paginator.num_pages,
                'total_count': total_count,
                'has_next': page_obj.has_next(),
                'has_previous': page_obj.has_previous()
            }
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })