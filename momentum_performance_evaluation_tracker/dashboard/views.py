from django.shortcuts import render, redirect  # Add redirect import
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from core.forms import SupervisorPasswordResetForm

@never_cache
@login_required(login_url='/login/')
def dashboard_home(request):
    # Extra check (optional, since @login_required is used)
    if not request.user.is_authenticated:
        return redirect('core:login')

    show_password_reset = False
    password_reset_form = None

    # Check if supervisor needs password reset
    if hasattr(request.user, 'role') and request.user.role.role_id == 302 and request.user.is_first_login:
        show_password_reset = True
        password_reset_form = SupervisorPasswordResetForm(user=request.user)
    
    context = {
        'user_account': request.user,
        'employee': request.user.employee,
        'show_password_reset': show_password_reset,
        'password_reset_form': password_reset_form,
    }
    return render(request, "dashboard/dashboard.html", context)
