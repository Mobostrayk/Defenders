from django.db import models
from django.contrib.auth.models import User
import uuid
from django.utils import timezone
from datetime import timedelta
from django.conf import settings

class TempRegistration(models.Model):
    username = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)
    verification_code = models.UUIDField(default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(default=timezone.now)

    def is_expired(self):
        expire_seconds = getattr(settings, 'VERIFICATION_CODE_EXPIRE_SECONDS', 7200)
        return (timezone.now() - self.created_at).total_seconds() > expire_seconds

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