from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.contrib.auth import authenticate
from .forms import CustomUserCreationForm

class CustomLoginView(LoginView):
    template_name = 'accounts/login.html'
    redirect_authenticated_user = True

    def form_valid(self, form):
        messages.success(self.request, f'Добро пожаловать, {form.get_user().first_name}!')
        return super().form_valid(form)

class CustomLogoutView(LogoutView):
    def dispatch(self, request, *args, **kwargs):
        messages.info(request, 'Вы успешно вышли из системы.')
        return super().dispatch(request, *args, **kwargs)

def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'Регистрация прошла успешно! Теперь вы можете войти в систему.')
            login(request, user)  # Автоматически входим после регистрации
            # Исправляем ссылку с 'home' на 'main:home'
            return redirect('main:home')
    else:
        form = CustomUserCreationForm()

    return render(request, 'accounts/register.html', {'form': form})


@csrf_exempt
def test_login_view(request):
    """Упрощённый login без CSRF для нагрузочного тестирования Locust.
    НЕ использовать в продакшене.
    Ожидает POST с полями `username` и `password` и логинит через Django auth.
    """
    if request.method != 'POST':
        return JsonResponse({'detail': 'Method not allowed'}, status=405)

    username = request.POST.get('username')
    password = request.POST.get('password')

    if not username or not password:
        return JsonResponse({'detail': 'Missing credentials'}, status=400)

    user = authenticate(request, username=username, password=password)
    if user is None:
        return JsonResponse({'detail': 'Invalid credentials'}, status=403)

    login(request, user)
    return JsonResponse({'detail': 'ok'}, status=200)
