from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate
from .forms import RegisterForm, LoginForm
from .models import Profile
from django.shortcuts import redirect
from django.contrib.auth import logout as auth_logout
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from users.models import UserHabit
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from .forms import RegisterForm, LoginForm, VerificationForm
from .models import User, Profile, EmailVerification
import json
from django.views.decorators.http import require_POST


def registration(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']

            # Сохраняем данные формы в сессии
            request.session['registration_data'] = {
                'username': form.cleaned_data['username'],
                'email': email,
                'password': form.cleaned_data['password1'],
            }

            # Создаем верификацию (теперь без user_data)
            verification = EmailVerification.create_verification(email)

            # Отправляем email
            send_mail(
                'Подтверждение email',
                f'Ваш код подтверждения: {verification.code}',
                settings.DEFAULT_FROM_EMAIL,
                [email],
                fail_silently=False,
            )

            return redirect('verify_email', email=email)
    else:
        form = RegisterForm()
    return render(request, 'users/registration.html', {'form': form})


def verify_email(request, email):
    try:
        verification = EmailVerification.objects.get(email=email)
    except EmailVerification.DoesNotExist:
        return redirect('registration')

    if request.method == 'POST':
        form = VerificationForm(request.POST)
        if form.is_valid():
            if form.cleaned_data['code'] == verification.code:
                # Достаем данные из сессии
                user_data = request.session.get('registration_data')

                if not user_data:
                    messages.error(request, 'Сессия истекла, зарегистрируйтесь снова')
                    return redirect('registration')

                # Создаем пользователя
                user = User.objects.create_user(
                    username=user_data['username'],
                    email=email,
                    password=user_data['password']
                )

                # Очищаем сессию
                del request.session['registration_data']
                verification.delete()

                login(request, user)
                return redirect('profile')
            else:
                messages.error(request, 'Неверный код подтверждения')
    else:
        form = VerificationForm()

    return render(request, 'users/verify_email.html', {
        'form': form,
        'email': email,
        'expires_at': verification.expires_at
    })


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
                messages.error(request, 'Неверные учетные данные')
    else:
        form = LoginForm()
    return render(request, 'users/login.html', {'form': form})

def logout(request):
    auth_logout(request)
    return redirect('index')

def check_email(request):
    email = request.GET.get('email', '')
    exists = User.objects.filter(email__iexact=email).exists()
    return JsonResponse({'exists': exists})

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


@require_POST
def resend_code(request):
    email = request.POST.get('email')
    try:
        verification = EmailVerification.objects.get(email=email)

        if not verification.can_resend():
            return JsonResponse({
                'success': False,
                'error': 'Повторный код можно запросить через 1 минуту'
            })

        # Обновляем код
        verification.code = str(uuid.uuid4())[:6].upper()
        verification.last_sent_time = timezone.now()
        verification.save()

        # Отправляем письмо
        send_mail(...)

        return JsonResponse({'success': True})
    except EmailVerification.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Email не найден'})


def check_username(request):
    username = request.GET.get('username', '')
    exists = User.objects.filter(username__iexact=username).exists()
    return JsonResponse({'exists': exists})



