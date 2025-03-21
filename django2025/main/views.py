from django.shortcuts import render
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from users.models import Habit, UserHabit
import random


# def index(request):
#     return render(request,'main/index.html')

def about(request):
    return render(request,'main/about.html')

@login_required
def index(request):
    # Получаем все привычки
    habits = Habit.objects.all()
    # Выбираем случайную привычку
    random_habit = random.choice(habits) if habits else None
    # Проверяем, есть ли уже эта привычка у пользователя
    has_habit = UserHabit.objects.filter(user=request.user, habit=random_habit).exists() if random_habit else False

    return render(request, 'main/index.html', {
        'random_habit': random_habit,
        'has_habit': has_habit,
    })

@login_required
def save_habit(request, habit_id):
    habit = get_object_or_404(Habit, id=habit_id)
    UserHabit.objects.get_or_create(user=request.user, habit=habit)
    messages.success(request, f'Привычка "{habit.name}" сохранена!')
    return redirect('index')
