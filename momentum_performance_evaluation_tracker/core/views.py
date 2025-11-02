from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth import logout as auth_logout

from .forms import SupervisorPasswordResetForm, LoginForm, RegistrationForm
from .models import UserAccount, Employee

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