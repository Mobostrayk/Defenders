from django.contrib import admin
from . import models
from .models import EmailVerification


admin.site.register(models.Profile)
admin.site.register(models.Habit)
admin.site.register(models.UserHabit)


@admin.register(EmailVerification)
class EmailVerificationAdmin(admin.ModelAdmin):
    list_display = ('email', 'code', 'created_at', 'expires_at', 'is_expired')
    list_filter = ('created_at',)
    search_fields = ('email', 'code')
    readonly_fields = ('created_at',)


    def is_expired(self, obj):
        return obj.is_expired()

    is_expired.boolean = True
    is_expired.short_description = 'Истёк?'

    fieldsets = (
        (None, {
            'fields': ('email', 'code')
        }),
        ('Даты', {
            'fields': ('created_at', 'expires_at'),
            'classes': ('collapse',)
        }),
    )

    list_per_page = 50  # Количество записей на странице

@admin.action(description='Удалить истёкшие записи')
def delete_expired(modeladmin, request, queryset):
    queryset.filter(expires_at__lt=timezone.now()).delete()

class EmailVerificationAdmin(admin.ModelAdmin):
    actions = [delete_expired]





