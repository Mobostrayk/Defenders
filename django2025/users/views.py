from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate
from django.core.mail import send_mail
from django.conf import settings
from .forms import RegisterForm, LoginForm
from .models import Profile
from django.shortcuts import redirect
from django.contrib.auth import logout as auth_logout
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from users.models import UserHabit
from django.http import JsonResponse
from django.contrib.auth.models import User
from .models import TempRegistration
import uuid

def user_login(request):
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('profile')
    else:
        form = LoginForm()
    return render(request, 'users/login.html', {'form': form})

def logout(request):
    auth_logout(request)
    return redirect('index')


@login_required
def profile(request):
    # Получаем профиль пользователя
    user_profile = Profile.objects.get(user=request.user)
    # Получаем все привычки пользователя
    user_habits = UserHabit.objects.filter(user=request.user).select_related('habit')

    return render(request, 'users/profile.html', {
        'profile': user_profile,  # Передаем профиль
        'user_habits': user_habits,  # Передаем привычки
    })


def check_username(request):
    username = request.GET.get('username', '')
    exists = User.objects.filter(username__iexact=username).exists()
    return JsonResponse({'exists': exists})


def check_email(request):
    email = request.GET.get('email', '')
    exists = User.objects.filter(email__iexact=email).exists()
    return JsonResponse({'exists': exists})


def registration(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            # Сохраняем во временную таблицу
            temp_reg = TempRegistration(
                username=form.cleaned_data['username'],
                email=form.cleaned_data['email'],
                password=form.cleaned_data['password1']
            )
            temp_reg.save()

            # Отправляем письмо с кодом
            send_mail(
                'Подтверждение регистрации',
                f'Ваш код подтверждения: {temp_reg.verification_code}',
                settings.DEFAULT_FROM_EMAIL,
                [form.cleaned_data['email']],
                fail_silently=False,
            )

            # Перенаправляем на страницу подтверждения
            return redirect('verify_email', email=form.cleaned_data['email'])
    else:
        form = RegisterForm()
    return render(request, 'users/registration.html', {'form': form})


def verify_email(request, email):
    if request.method == 'POST':
        code = request.POST.get('code')
        try:
            temp_reg = TempRegistration.objects.get(email=email, verification_code=code)
            if temp_reg.is_expired():
                return render(request, 'users/verify_email.html', {
                    'email': email,
                    'error': 'Срок действия кода истёк. Пожалуйста, зарегистрируйтесь снова.'
                })

            # Создаем пользователя
            user = User.objects.create_user(
                username=temp_reg.username,
                email=temp_reg.email,
                password=temp_reg.password
            )

            # Удаляем временную запись
            temp_reg.delete()

            # Авторизуем пользователя
            user = authenticate(username=temp_reg.username, password=temp_reg.password)
            login(request, user)

            return redirect('profile')
        except TempRegistration.DoesNotExist:
            return render(request, 'users/verify_email.html', {
                'email': email,
                'error': 'Неверный код подтверждения'
            })

    return render(request, 'users/verify_email.html', {'email': email})


