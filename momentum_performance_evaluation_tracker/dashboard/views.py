# dashboard/views.py
from django.shortcuts import render 
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache

@never_cache # Prevent caching to ensure fresh data
@login_required(login_url='/login/')
def dashboard_home(request):
    
    # Extra check (optional, since @login_required is used)
    if not request.user.is_authenticated:
        return redirect('core:login')

    # Now request.user will be your logged-in UserAccount
    context = {
        'user_account': request.user,
        'employee': request.user.employee
    }
    return render(request, "dashboard/dashboard.html", context)