from datetime import timedelta
from django.utils import timezone
from .models import Achievement, HabitCompletion
from django.contrib.auth import get_user_model

def check_achievements(user):
    """
    Проверяет достижения пользователя и выдаёт их, если условия выполнены.
    """
    # Сортировка завершений по дате
    completions = HabitCompletion.objects.filter(user_habit__user=user).order_by('-date')

    # 1. Первое действие — Завести первую привычку
    if not Achievement.objects.filter(user=user, name="Первый шаг").exists():
        if completions.exists():
            Achievement.objects.create(
                user=user,
                name="Первый шаг",
                description="Заведите свою первую привычку",
                icon="users/achievements/first_step.png"
            )

    # 2. Неделя успеха — Выполнить 7 дней подряд
    if not Achievement.objects.filter(user=user, name="Неделя успеха").exists():
        streak = 0
        current_date = timezone.now().date()
        for i in range(7):  # Проверяем последние 7 дней
            day = current_date - timedelta(days=i)
            if completions.filter(date=day).exists():
                streak += 1
            else:
                break
        if streak >= 7:
            Achievement.objects.create(
                user=user,
                name="Неделя успеха",
                description="Выполнить 7 дней подряд",
                icon="users/achievements/week_streak.png"
            )

    # 3. Месяц непрерывности — 30 дней с отметками
    if not Achievement.objects.filter(user=user, name="Месяц непрерывности").exists():
        total_days = completions.values('date').distinct().count()
        if total_days >= 30:
            Achievement.objects.create(
                user=user,
                name="Месяц непрерывности",
                description="Отметить привычки 30 дней за весь период",
                icon="users/achievements/month_streak.png"
            )

    # 4. Мастер привычек — 5 активных привычек
    if not Achievement.objects.filter(user=user, name="Мастер привычек").exists():
        active_habits = user.userhabit_set.count()
        if active_habits >= 5:
            Achievement.objects.create(
                user=user,
                name="Мастер привычек",
                description="Создать 5 активных привычек",
                icon="users/achievements/master_habits.png"
            )


    # 6. Легенда — 100 дней без пропусков
    if not Achievement.objects.filter(user=user, name="Легенда").exists():
        streak = 0
        current_day = timezone.now().date()
        while completions.filter(date=current_day).exists():
            streak += 1
            current_day -= timedelta(days=1)

        if streak >= 100:
            Achievement.objects.create(
                user=user,
                name="Легенда",
                description="100 дней без пропусков",
                icon="users/achievements/legend.png"
            )

    # 7. Универсальный герой — выполнять привычки в выходные
    if not Achievement.objects.filter(user=user, name="Универсальный герой").exists():
        weekend_completions = completions.filter(date__week_day__in=[0, 6])  # Воскресенье = 0, Суббота = 6
        if weekend_completions.exists():
            Achievement.objects.create(
                user=user,
                name="Универсальный герой",
                description="Выполнить любую привычку в выходной день",
                icon="users/achievements/weekend_hero.png"
            )

    # 8. Ранняя пташка — выполнение до 9 утра
    if not Achievement.objects.filter(user=user, name="Ранняя пташка").exists():
        early_completions = completions.filter(date__lt=timezone.make_aware(timezone.datetime.combine(
            timezone.now().date(), timezone.datetime.min.time()
        ) + timedelta(hours=9)))
        if early_completions.exists():
            Achievement.objects.create(
                user=user,
                name="Ранняя пташка",
                description="Выполнить привычку до 9:00",
                icon="users/achievements/early_bird.png"
            )