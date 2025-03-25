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


def registration(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect('profile')
    else:
        form = RegisterForm()
    return render(request, 'users/registration.html', {'form': form})

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



