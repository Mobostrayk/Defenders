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
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils import timezone
from datetime import timedelta
from .models import UserHabit, HabitCompletion
from .forms import HabitSettingsForm


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


@login_required
def track_habits(request):
    today = timezone.now().date()
    user_habits = UserHabit.objects.filter(user=request.user).select_related('habit')

    # Получаем привычки для сегодня
    today_habits = []
    for user_habit in user_habits:
        if today.weekday() in user_habit.get_selected_days():
            completion, created = HabitCompletion.objects.get_or_create(
                user_habit=user_habit,
                date=today,
                defaults={'completed': False}
            )
            today_habits.append({
                'user_habit': user_habit,
                'completion': completion
            })

    # Получаем историю за последние 7 дней
    history = []
    for i in range(7):
        date = today - timedelta(days=i)
        habits_for_day = []
        for user_habit in user_habits:
            if date.weekday() in user_habit.get_selected_days():
                try:
                    completion = HabitCompletion.objects.get(user_habit=user_habit, date=date)
                    habits_for_day.append({
                        'habit': user_habit.habit.name,
                        'completed': completion.completed
                    })
                except HabitCompletion.DoesNotExist:
                    habits_for_day.append({
                        'habit': user_habit.habit.name,
                        'completed': False
                    })
        history.append({
            'date': date,
            'habits': habits_for_day
        })

    return render(request, 'users/track_habits.html', {
        'today_habits': today_habits,
        'history': history
    })


@login_required
def update_habit_completion(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        habit_id = data.get('habit_id')
        date_str = data.get('date')
        completed = data.get('completed')

        try:
            date = timezone.datetime.strptime(date_str, '%Y-%m-%d').date()
            user_habit = UserHabit.objects.get(id=habit_id, user=request.user)

            # Проверяем, что дата не более чем на 1 день в будущем
            today = timezone.now().date()
            if date > today + timedelta(days=1):
                return JsonResponse(
                    {'status': 'error', 'message': 'Нельзя отмечать привычки более чем на 1 день вперед'})

            # Обновляем или создаем запись
            completion, created = HabitCompletion.objects.get_or_create(
                user_habit=user_habit,
                date=date,
                defaults={'completed': completed}
            )
            if not created:
                completion.completed = completed
                completion.save()

            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})

    return JsonResponse({'status': 'error', 'message': 'Invalid request'})


@login_required
def habit_settings(request, habit_id):
    user_habit = get_object_or_404(UserHabit, id=habit_id, user=request.user)

    if request.method == 'POST':
        form = HabitSettingsForm(request.POST, instance=user_habit)
        if form.is_valid():
            form.save()
            return redirect('track_habits')
    else:
        form = HabitSettingsForm(instance=user_habit)

    return render(request, 'users/habit_settings.html', {
        'form': form,
        'habit': user_habit.habit
    })


@login_required
def habit_stats(request, habit_id):
    user_habit = get_object_or_404(UserHabit, id=habit_id, user=request.user)
    today = timezone.now().date()

    # Получаем все выполнения привычки
    completions = HabitCompletion.objects.filter(
        user_habit=user_habit,
        date__lte=today
    ).order_by('-date')

    # Подсчет статистики
    total_days = completions.count()
    completed_days = completions.filter(completed=True).count()

    # Подсчет текущей серии
    current_streak = 0
    for completion in completions:
        if completion.completed:
            current_streak += 1
        else:
            break

    return render(request, 'users/habit_stats.html', {
        'user_habit': user_habit,
        'total_days': total_days,
        'completed_days': completed_days,
        'current_streak': current_streak,
        'completions': completions[:30]  # Последние 30 дней
    })


