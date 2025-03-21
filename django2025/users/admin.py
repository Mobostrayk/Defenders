from django.contrib import admin
from . import models

admin.site.register(models.Profile)
admin.site.register(models.Habit)
admin.site.register(models.UserHabit)

