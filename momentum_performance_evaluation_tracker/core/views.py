# from django.shortcuts import render

# # Create your views here.
# def home_page(request):
#     return render(request, 'core/home.html')

from django.shortcuts import render, redirect
from django.http import HttpResponse
from supabase import create_client, Client
from django.contrib import messages
import os

SUPABASE_URL = os.getenv("SUPABASE_URL", "https://daskjodohjfnrrrpdplu.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImRhc2tqb2RvaGpmbnJycnBkcGx1Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTk0NTI5NzYsImV4cCI6MjA3NTAyODk3Nn0.um6x9lnIHuc9vZO3u9QUYU6x9QeGQt5sBBhetViliZo")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


def home_page(request):
    return render(request, "core/home.html")

def login_page(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        response = (
            supabase.table("UserAccount")
            .select("*")
            .eq("username", username)
            .execute()
        )

        print("DEBUG raw response:", response)

        if response.data:
            user = response.data[0]
            if user["password"] == password:
                return redirect("core:dashboard")
            else:
                messages.error(request, "Invalid password")
                return render(request, "core/home.html", {"show_login": True})
        else:
            messages.error(request, "User not found")
            return render(request, "core/home.html", {"show_login": True})

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

        email_check = supabase.table("Employee").select("email_address").eq("email_address", email_address).execute()
        if email_check.data:
            messages.error(request, "Email address already in use.")
            return render(request, "core/home.html", {"show_register": True})
        
        username_check = supabase.table("UserAccount").select("username").eq("username", username).execute()
        if username_check.data:
            messages.error(request, "Username already exists.")
            return render(request, "core/home.html", {"show_register": True})

        try: 
            employee_response = supabase.table("Employee").insert({
                "first_name": first_name,
                "last_name": last_name,
                "department": department,
                "position": position,
                "hire_date": hire_date,
                "email_address": email_address
            }).execute()

            if not employee_response.data:
                messages.error(request, "Error creating employee record.")
                return render(request, "core/home.html", {"show_register": True})

            employee_id = employee_response.data[0]["employee_id"]

            supabase.table("UserAccount").insert({
                "employee_id": employee_id,
                "username": username,
                "password": password,
                "role_id": 303
            }).execute()

            messages.success(request, "Account created successfully! Please login.")
            return render(request, "core/home.html", {"show_login": True})
        
        except Exception as e:
            print("Error during registration:", e)
            messages.error(request, "An error occurred during registration. Please try again.")
            return render(request, "core/home.html", {"show_register": True})

    return redirect("core:home")