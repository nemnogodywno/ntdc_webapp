from django.shortcuts import render
from django.contrib.auth.decorators import login_required

def home_view(request):
    """Главная страница - доступна всем"""
    return render(request, 'main/home.html')

@login_required
def dashboard_view(request):
    """Панель управления - только для авторизованных"""
    context = {
        'user': request.user,
        'is_admin': request.user.is_admin_user() if hasattr(request.user, 'is_admin_user') else False
    }
    return render(request, 'main/dashboard.html', context)

@login_required
def admin_panel_view(request):
    """Админ панель - только для администраторов"""
    if not (hasattr(request.user, 'is_admin_user') and request.user.is_admin_user()):
        return render(request, 'main/access_denied.html', status=403)

    return render(request, 'main/admin_panel.html')
