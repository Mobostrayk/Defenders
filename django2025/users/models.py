
from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)

    def __str__(self):
        return self.user.username


class Habit(models.Model):
    name = models.CharField(max_length=255, unique=True)  # Название привычки

    def __str__(self):
        return self.name

class UserHabit(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Пользователь
    habit = models.ForeignKey(Habit, on_delete=models.CASCADE)  # Привычка
    created_at = models.DateTimeField(auto_now_add=True)  # Дата добавления

    class Meta:
        unique_together = ('user', 'habit')  # Уникальная связь пользователя и привычки

    def __str__(self):
        return f"{self.user.username} - {self.habit.name}"