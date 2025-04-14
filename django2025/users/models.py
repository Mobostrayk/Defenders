from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import uuid
from django.contrib.auth.models import AbstractUser


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)

    def __str__(self):
        return self.user.username


class Habit(models.Model):
    name = models.CharField(max_length=255, unique=True)
    is_fixed = models.BooleanField(default=False)  # Фиксированная привычка (все дни)
    weekend_only = models.BooleanField(default=False)  # Только выходные

    def __str__(self):
        return self.name


class UserHabit(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    habit = models.ForeignKey(Habit, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    # Дни недели для привычки (0-пн, 1-вт, ..., 6-вс)
    monday = models.BooleanField(default=False)
    tuesday = models.BooleanField(default=False)
    wednesday = models.BooleanField(default=False)
    thursday = models.BooleanField(default=False)
    friday = models.BooleanField(default=False)
    saturday = models.BooleanField(default=False)
    sunday = models.BooleanField(default=False)

    class Meta:
        unique_together = ('user', 'habit')

    def __str__(self):
        return f"{self.user.username} - {self.habit.name}"

    def get_selected_days(self):
        """Возвращает список выбранных дней недели"""
        days = []
        if self.monday: days.append(0)
        if self.tuesday: days.append(1)
        if self.wednesday: days.append(2)
        if self.thursday: days.append(3)
        if self.friday: days.append(4)
        if self.saturday: days.append(5)
        if self.sunday: days.append(6)
        return days


class HabitCompletion(models.Model):
    user_habit = models.ForeignKey(UserHabit, on_delete=models.CASCADE)
    date = models.DateField()
    completed = models.BooleanField(default=False)

    class Meta:
        unique_together = ('user_habit', 'date')

    def __str__(self):
        return f"{self.user_habit} - {self.date} - {'Выполнено' if self.completed else 'Не выполнено'}"


class EmailVerification(models.Model):
    email = models.EmailField(unique=True)
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    def is_expired(self):
        return timezone.now() > self.expires_at

    @classmethod
    def create_verification(cls, email):
        cls.objects.filter(email=email).delete()
        return cls.objects.create(
            email=email,
            code=str(uuid.uuid4())[:6].upper(),
            expires_at=timezone.now() + timezone.timedelta(hours=1),
        )

