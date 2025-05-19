from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate
from .forms import RegisterForm, LoginForm, PasswordResetConfirmForm, PasswordResetForm
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
import pytz
from django.conf import settings
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login
from django.core.mail import send_mail
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
import requests
from .forms import RegisterForm, VerificationForm
from .models import EmailVerification, User
from captcha.fields import CaptchaField
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib import messages
from django.shortcuts import redirect
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils import timezone
from .models import EmailVerification
import random
import string
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError



def registration(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']

            # Удаляем старые верификации перед созданием новой
            EmailVerification.objects.filter(email=email).delete()

            # Создаем новую верификацию
            verification = EmailVerification.create_verification(email)

            # Сохраняем данные в сессии
            request.session['registration_data'] = {
                'username': form.cleaned_data['username'],
                'email': email,
                'password': form.cleaned_data['password1'],
            }

            # Отправляем письмо
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


RECAPTCHA_SECRET = '6LcOiz0rAAAAAOcE0G9Uidk__qWIdvCDASLQUUAE'
def verify_recaptcha(token):
    data = {
        'secret': RECAPTCHA_SECRET,
        'response': token
    }
    response = requests.post('https://www.google.com/recaptcha/api/siteverify', data=data)
    return response.json().get('success', False)


@require_POST
def resend_code(request):
    email = request.POST.get('email')
    try:
        # Удаляем старую верификацию
        EmailVerification.objects.filter(email=email).delete()

        # Создаем новую
        verification = EmailVerification.create_verification(email)

        # Отправляем письмо (ваш код отправки email)

        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


def verify_email(request, email):
    try:
        verification = EmailVerification.objects.get(email=email)
        remaining_time = verification.expires_at - timezone.now()
        remaining_seconds = max(0, int(remaining_time.total_seconds()))
        minutes = remaining_seconds // 60
        seconds = remaining_seconds % 60
    except EmailVerification.DoesNotExist:
        return redirect('registration')

    if request.method == 'POST':
        form = VerificationForm(request.POST)
        if form.is_valid():
            if form.cleaned_data['code'] == verification.code:
                user_data = request.session.get('registration_data')

                if not user_data:
                    messages.error(request, 'Сессия истекла, зарегистрируйтесь снова')
                    return redirect('registration')

                try:
                    # Создаем пользователя
                    user = User.objects.create_user(
                        username=user_data['username'],
                        email=email,
                        password=user_data['password']
                    )

                    # Авторизуем сразу
                    user = authenticate(
                        username=user_data['username'],
                        password=user_data['password']
                    )
                    login(request, user)

                    # Очищаем данные
                    del request.session['registration_data']
                    verification.delete()

                    return redirect('profile')

                except Exception as e:
                    messages.error(request, f'Ошибка: {str(e)}')
                    return redirect('registration')
            else:
                messages.error(request, 'Неверный код подтверждения')
    else:
        form = VerificationForm()

    return render(request, 'users/verify_email.html', {
        'form': form,
        'email': email,
        'minutes': minutes,
        'seconds': f"{seconds:02d}",
        'remaining_seconds': remaining_seconds
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
    # Настройка часового пояса
    tz = pytz.timezone(settings.TIME_ZONE)

    # Обработка параметров даты
    date_str = request.GET.get('date')
    if date_str:
        try:
            current_date = timezone.datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            current_date = timezone.now().astimezone(tz).date()
    else:
        current_date = timezone.now().astimezone(tz).date()

    # Обработка недельного смещения
    week_offset = int(request.GET.get('week_offset', 0))
    week_start = current_date - timedelta(days=current_date.weekday()) + timedelta(weeks=week_offset)
    week_end = week_start + timedelta(days=6)

    # Получаем привычки пользователя
    user_habits = UserHabit.objects.filter(user=request.user).select_related('habit')

    # Привычки для текущей даты
    habits_for_date = []
    for user_habit in user_habits:
        # Проверяем, что привычка уже существовала на эту дату
        if current_date < user_habit.created_at.date():
            continue

        if current_date.weekday() in user_habit.get_selected_days():
            try:
                completion = HabitCompletion.objects.get(
                    user_habit=user_habit,
                    date=current_date
                )
                completed = completion.completed
            except HabitCompletion.DoesNotExist:
                completed = False

            yesterday = current_date - timedelta(days=1)
            overdue = (current_date < yesterday) and not completed

            habits_for_date.append({
                'id': user_habit.id,
                'name': user_habit.habit.name,
                'completed': completed,
                'overdue': overdue
            })

    # Формируем данные для недельного календаря
    week_days = []
    for i in range(7):
        day_date = week_start + timedelta(days=i)
        day_habits = []
        day_completions = []

        for user_habit in user_habits:
            # Пропускаем привычки, которых еще не было в этот день
            if day_date < user_habit.created_at.date():
                continue

            if day_date.weekday() in user_habit.get_selected_days():
                try:
                    completion = HabitCompletion.objects.get(
                        user_habit=user_habit,
                        date=day_date
                    )
                    day_completions.append(completion.completed)
                except HabitCompletion.DoesNotExist:
                    day_completions.append(False)

        # Определяем статус дня только для существовавших привычек
        has_habits = len(day_completions) > 0
        all_completed = has_habits and all(day_completions)
        some_completed = has_habits and any(day_completions) and not all_completed

        week_days.append({
            'date': day_date,
            'has_habits': has_habits,
            'all_completed': all_completed,
            'some_completed': some_completed
        })

    return render(request, 'users/track_habits.html', {
        'current_date': current_date,
        'habits': habits_for_date,
        'week_start': week_start,
        'week_end': week_end,
        'week_days': week_days,
        'week_offset': week_offset
    })


@login_required
def update_habit_completion(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        habit_id = data.get('habit_id')
        date_str = data.get('date')
        completed = data.get('completed')

        try:
            # Получаем текущую дату с учетом часового пояса
            tz = pytz.timezone(settings.TIME_ZONE)
            now = timezone.now().astimezone(tz)
            today = now.date()
            last_allowed_date = today - timedelta(days=6)  # Разрешаем отмечать за последние 7 дней

            date = timezone.datetime.strptime(date_str, '%Y-%m-%d').date()
            user_habit = UserHabit.objects.get(id=habit_id, user=request.user)

            # Проверяем что дата не в будущем
            if date > today:
                return JsonResponse(
                    {'status': 'error', 'message': 'Нельзя отмечать привычки за будущие даты'})

            # Проверяем что дата не раньше чем 6 дней назад
            if date < last_allowed_date:
                return JsonResponse(
                    {'status': 'error', 'message': 'Можно отмечать привычки только за последние 7 дней'})

            # Проверяем что привычка должна выполняться в этот день
            selected_days = user_habit.get_selected_days()
            if date.weekday() not in selected_days:
                return JsonResponse(
                    {'status': 'error', 'message': 'Эта привычка не выполняется в выбранный день'})

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
        'user_habit': user_habit,
        'form': form,
        'habit': user_habit.habit
    })


@login_required
def habit_stats(request, habit_id):
    user_habit = get_object_or_404(UserHabit, id=habit_id, user=request.user)
    today = timezone.localtime(timezone.now()).date()

    # Получаем все выполнения привычки (включая сегодняшний день)
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
        'completion_percentage': round((completed_days / total_days) * 100) if total_days > 0 else 0,
        'completions': completions[:30]  # Последние 30 дней
    })


@login_required
def delete_habit(request, habit_id):
    if request.method == 'POST':
        try:
            user_habit = UserHabit.objects.get(id=habit_id, user=request.user)
            user_habit.delete()
            return JsonResponse({'status': 'success'})
        except UserHabit.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Привычка не найдена'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    return JsonResponse({'status': 'error', 'message': 'Неверный метод запроса'})


@login_required
def update_profile(request):
    if request.method == 'POST':
        # Обработка аватара
        if 'avatar' in request.FILES:
            profile = Profile.objects.get(user=request.user)
            profile.avatar = request.FILES['avatar']
            profile.save()
            messages.success(request, 'Аватар успешно обновлен')

        # Обработка смены пароля
        old_password = request.POST.get('old_password')
        new_password1 = request.POST.get('new_password1')
        new_password2 = request.POST.get('new_password2')

        if old_password and new_password1 and new_password2:
            if new_password1 != new_password2:
                messages.error(request, 'Новые пароли не совпадают')
            else:
                user = request.user
                if user.check_password(old_password):
                    user.set_password(new_password1)
                    user.save()
                    update_session_auth_hash(request, user)  # Чтобы пользователь не разлогинился
                    messages.success(request, 'Пароль успешно изменен')
                else:
                    messages.error(request, 'Неверный текущий пароль')

        return redirect('profile')

    return redirect('profile')


@login_required
def update_avatar(request):
    if request.method == 'POST' and request.FILES.get('avatar'):
        profile = request.user.profile
        profile.avatar = request.FILES['avatar']
        profile.save()
        return JsonResponse({
            'status': 'success',
            'avatar_url': profile.avatar.url
        })
    return JsonResponse({'status': 'error', 'message': 'Неверный запрос'})


@login_required
def update_password(request):
    if request.method == 'POST':
        old_password = request.POST.get('old_password')
        new_password1 = request.POST.get('new_password1')
        new_password2 = request.POST.get('new_password2')

        if not (old_password and new_password1 and new_password2):
            return JsonResponse({'status': 'error', 'message': 'Заполните все поля'})

        if new_password1 != new_password2:
            return JsonResponse({'status': 'error', 'message': 'Пароли не совпадают'})

        if len(new_password1) < 8:
            return JsonResponse({'status': 'error', 'message': 'Пароль должен содержать минимум 8 символов'})

        user = request.user
        if user.check_password(old_password):
            user.set_password(new_password1)
            user.save()
            update_session_auth_hash(request, user)
            return JsonResponse({'status': 'success'})
        else:
            return JsonResponse({'status': 'error', 'message': 'Неверный текущий пароль'})

    return JsonResponse({'status': 'error', 'message': 'Неверный метод запроса'})


User = get_user_model()

User = get_user_model()


def password_reset_request(request):
    if request.method == 'POST':
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            if User.objects.filter(email=email).exists():
                # Генерируем код
                code = ''.join(random.choices(string.digits, k=6))
                expires_at = timezone.now() + timezone.timedelta(minutes=15)

                # Сохраняем код
                EmailVerification.objects.update_or_create(
                    email=email,
                    defaults={'code': code, 'expires_at': expires_at}
                )

                # В реальном проекте отправьте email здесь
                print(f"Код для сброса пароля ({email}): {code}")
                send_mail(
                    subject='Код для сброса пароля',
                    message=f'Ваш код подтверждения: {code}\nКод действителен 15 минут.',
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[email],
                    fail_silently=False,
                )

                return redirect('password_reset_confirm', email=email)
            else:
                messages.error(request, 'Пользователь с таким email не найден')
    else:
        form = PasswordResetForm()

    return render(request, 'users/password_reset.html', {'form': form})


def password_reset_confirm(request, email):
    verification = get_object_or_404(EmailVerification, email=email)

    if request.method == 'POST':
        form = PasswordResetConfirmForm(request.POST)
        if form.is_valid():
            # Проверяем код
            if form.cleaned_data['code'] != verification.code:
                form.add_error('code', 'Неверный код')
            elif timezone.now() > verification.expires_at:
                form.add_error('code', 'Срок действия кода истек')
            elif form.cleaned_data['new_password'] != form.cleaned_data['confirm_password']:
                form.add_error('confirm_password', 'Пароли не совпадают')
            else:
                # Все проверки пройдены - меняем пароль
                user = User.objects.get(email=email)
                user.set_password(form.cleaned_data['new_password'])
                user.save()

                # Автологин
                user = authenticate(
                    username=user.username,
                    password=form.cleaned_data['new_password']
                )
                login(request, user)

                # Удаляем код
                verification.delete()

                messages.success(request, 'Пароль успешно изменен!')
                return redirect('profile')
    else:
        form = PasswordResetConfirmForm()

    # Таймер
    remaining_time = verification.expires_at - timezone.now()
    remaining_seconds = max(0, int(remaining_time.total_seconds()))

    return render(request, 'users/password_reset_confirm.html', {
        'form': form,
        'email': email,
        'minutes': remaining_seconds // 60,
        'seconds': f"{remaining_seconds % 60:02d}",
        'remaining_seconds': remaining_seconds
    })