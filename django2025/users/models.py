from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import uuid
from django.contrib.auth.models import AbstractUser




# Оставляем существующие модели без изменений
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)

    def __str__(self):
        return self.user.username


class Habit(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name


class UserHabit(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    habit = models.ForeignKey(Habit, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'habit')

    def __str__(self):
        return f"{self.user.username} - {self.habit.name}"


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