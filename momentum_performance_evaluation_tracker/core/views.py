from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib import messages
from django.db import transaction

from .models import Role, Employee, UserAccount

def home_page(request):
    return render(request, "core/home.html")

def login_page(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = UserAccount.objects.filter(username__iexact=username).first()
        if not user:
            messages.error(request, "User not found")
            return render(request, "core/home.html", {"show_login": True})

        # use models.py's check_password
        if not user.check_password(password):
            messages.error(request, "Invalid password")
            return render(request, "core/home.html", {"show_login": True})

        return redirect("core:dashboard")

    return redirect("core:home")


def dashboard(request):
    return render(request, "dashboard/dashboard.html")


def registration(request):
    if request.method == "POST":
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        email_address = request.POST.get("email")
        hire_date = request.POST.get("date_hired")
        position = request.POST.get("position")
        department = request.POST.get("department")
        username = request.POST.get("username")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")

        if password != confirm_password:
            messages.error(request, "Passwords do not match!")
            return render(request, "core/home.html", {"show_register": True})

        if Employee.objects.filter(email_address__iexact=email_address).exists():
            messages.error(request, "Email address already in use.")
            return render(request, "core/home.html", {"show_register": True})

        if UserAccount.objects.filter(username__iexact=username).exists():
            messages.error(request, "Username already exists.")
            return render(request, "core/home.html", {"show_register": True})

        # get role (use primary key 303 for Employee)
        role = Role.objects.filter(pk=303).first()
        if not role:
            role, _ = Role.objects.get_or_create(role_id=303, defaults={"role_name": "Employee", "description": "Standard employee"})

        try:
            with transaction.atomic():
                employee = Employee.objects.create(
                    first_name=first_name,
                    last_name=last_name,
                    department=department,
                    position=position,
                    hire_date=hire_date or None,
                    email_address=email_address
                )
                user = UserAccount(
                    employee=employee,
                    username=username,
                    role=role
                )
                user.set_password(password)
                user.save()

            messages.success(request, "Account created successfully! Please login.")
            return render(request, "core/home.html", {"show_login": True})
        except Exception as e:
            print("Error during registration:", e)
            messages.error(request, "An error occurred during registration. Please try again.")
            return render(request, "core/home.html", {"show_register": True})

    return redirect("core:home")


def check_email_exists(request):
    email = request.GET.get("email")
    exists = False
    if email:
        exists = Employee.objects.filter(email_address__iexact=email).exists()
    return JsonResponse({"exists": exists})


def check_username_exists(request):
    username = request.GET.get("username")
    exists = False
    if username:
        exists = UserAccount.objects.filter(username__iexact=username).exists()
    return JsonResponse({"exists": exists})