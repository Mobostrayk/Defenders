from django.shortcuts import render
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from users.models import Habit, UserHabit
import random

from users.forms import HabitDaysForm


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

    # Проверяем, есть ли уже такая привычка у пользователя
    if UserHabit.objects.filter(user=request.user, habit=habit).exists():
        messages.info(request, f'Привычка "{habit.name}" уже сохранена!')
        return redirect('index')

    if request.method == 'POST':
        # Если привычка фиксированная, сохраняем все дни
        if habit.is_fixed:
            user_habit = UserHabit.objects.create(
                user=request.user,
                habit=habit,
                monday=True,
                tuesday=True,
                wednesday=True,
                thursday=True,
                friday=True,
                saturday=True,
                sunday=True
            )
            messages.success(request, f'Привычка "{habit.name}" сохранена!')
            return redirect('profile')

        # Если не фиксированная, обрабатываем форму
        form = HabitDaysForm(request.POST)
        if form.is_valid():
            user_habit = form.save(commit=False)
            user_habit.user = request.user
            user_habit.habit = habit
            user_habit.save()
            messages.success(request, f'Привычка "{habit.name}" сохранена!')
            return redirect('profile')
    else:
        # Для фиксированных привычек сразу сохраняем
        if habit.is_fixed:
            user_habit = UserHabit.objects.create(
                user=request.user,
                habit=habit,
                monday=True,
                tuesday=True,
                wednesday=True,
                thursday=True,
                friday=True,
                saturday=True,
                sunday=True
            )
            messages.success(request, f'Привычка "{habit.name}" сохранена!')
            return redirect('profile')

        # Для остальных показываем форму выбора дней
        initial = {}
        if habit.weekend_only:
            initial = {'saturday': True, 'sunday': True}
        else:
            initial = {
                'monday': True,
                'tuesday': True,
                'wednesday': True,
                'thursday': True,
                'friday': True,
                'saturday': True,
                'sunday': True
            }

        form = HabitDaysForm(initial=initial)

    return render(request, 'main/save_habit.html', {
        'habit': habit,
        'form': form,
        'is_fixed': habit.is_fixed
    })
