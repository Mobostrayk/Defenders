from django.shortcuts import render
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from users.models import Habit, UserHabit
import random


def about(request):
    return render(request,'main/about.html')


def index(request):
    # Получаем все привычки
    habits = Habit.objects.all()

    if habits.exists():  # Если есть привычки в базе
        # Если пользователь авторизован, исключаем его сохраненные привычки
        if request.user.is_authenticated:
            user_habits = UserHabit.objects.filter(user=request.user).values_list('habit_id', flat=True)
            available_habits = habits.exclude(id__in=user_habits)
        else:
            available_habits = habits  # Для неавторизованных пользователей все привычки доступны

        if available_habits.exists():  # Если есть доступные привычки
            random_habit = random.choice(available_habits)  # Выбираем случайную привычку
            has_habit = False
        else:
            random_habit = None  # Нет доступных привычек
            has_habit = True
    else:
        random_habit = None  # Нет привычек в базе
        has_habit = False

    return render(request, 'main/index.html', {
        'random_habit': random_habit,
        'has_habit': has_habit,
        'habits_exist': habits.exists(),  # Передаем информацию о наличии привычек
    })


@login_required(login_url='login')
def save_habit(request, habit_id):
    habit = get_object_or_404(Habit, id=habit_id)
    user_habit, created = UserHabit.objects.get_or_create(user=request.user, habit=habit)

    # Если привычка новая, устанавливаем дни по умолчанию
    if created:
        if habit.is_fixed:
            # Все дни для фиксированных привычек
            user_habit.monday = True
            user_habit.tuesday = True
            user_habit.wednesday = True
            user_habit.thursday = True
            user_habit.friday = True
            user_habit.saturday = True
            user_habit.sunday = True
        elif habit.weekend_only:
            # Только выходные
            user_habit.saturday = True
            user_habit.sunday = True
        else:
            # По умолчанию - все дни
            user_habit.monday = True
            user_habit.tuesday = True
            user_habit.wednesday = True
            user_habit.thursday = True
            user_habit.friday = True
            user_habit.saturday = True
            user_habit.sunday = True
        user_habit.save()

    messages.success(request, f'Привычка "{habit.name}" сохранена!')
    return redirect('index')
