from django.contrib import admin
from django.utils import timezone
from .models import Profile, Habit, UserHabit, EmailVerification

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'avatar_preview')
    list_select_related = ('user',)
    search_fields = ('user__username', 'user__email')
    readonly_fields = ('avatar_preview',)
    list_per_page = 20

    def avatar_preview(self, obj):
        if obj.avatar:
            return f'<img src="{obj.avatar.url}" style="max-height: 50px; max-width: 50px;" />'
        return "Нет аватара"
    avatar_preview.short_description = 'Превью'
    avatar_preview.allow_tags = True

    fieldsets = (
        ('Основное', {
            'fields': ('user', 'avatar', 'avatar_preview')
        }),
    )

@admin.register(Habit)
class HabitAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_fixed', 'weekend_only')
    list_filter = ('is_fixed', 'weekend_only')
    search_fields = ('name',)
    list_editable = ('is_fixed', 'weekend_only')
    list_per_page = 30

    fieldsets = (
        ('Основное', {
            'fields': ('name',)
        }),
        ('Настройки', {
            'fields': ('is_fixed', 'weekend_only'),
            'description': 'Фиксированные привычки отображаются каждый день, weekend_only - только по выходным'
        }),
    )

@admin.register(UserHabit)
class UserHabitAdmin(admin.ModelAdmin):
    list_display = ('user', 'habit', 'days_display', 'completion_rate')
    list_filter = ('habit__is_fixed', 'habit__weekend_only')
    search_fields = ('user__username', 'habit__name')
    list_select_related = ('user', 'habit')
    list_per_page = 25

    def days_display(self, obj):
        days = []
        if obj.monday: days.append('Пн')
        if obj.tuesday: days.append('Вт')
        if obj.wednesday: days.append('Ср')
        if obj.thursday: days.append('Чт')
        if obj.friday: days.append('Пт')
        if obj.saturday: days.append('Сб')
        if obj.sunday: days.append('Вс')
        return ', '.join(days) if days else 'Нет дней'
    days_display.short_description = 'Дни'

    def completion_rate(self, obj):
        from django.db.models import Count, Q
        completions = obj.habitcompletion_set.aggregate(
            total=Count('id'),
            completed=Count('id', filter=Q(completed=True))
        )
        if completions['total'] > 0:
            return f"{completions['completed']}/{completions['total']} ({completions['completed']/completions['total']:.0%})"
        return "Нет данных"
    completion_rate.short_description = 'Выполнение'

    fieldsets = (
        ('Основное', {
            'fields': ('user', 'habit')
        }),
        ('Расписание', {
            'fields': (
                ('monday', 'tuesday', 'wednesday'),
                ('thursday', 'friday', 'saturday', 'sunday')
            )
        }),
    )

@admin.register(EmailVerification)
class EmailVerificationAdmin(admin.ModelAdmin):
    list_display = ('email', 'code', 'created_at', 'expires_at', 'is_expired', 'time_remaining')
    list_filter = ('created_at', 'expires_at')
    search_fields = ('email', 'code')
    readonly_fields = ('created_at', 'is_expired', 'time_remaining')
    list_per_page = 50

    def is_expired(self, obj):
        return obj.is_expired()
    is_expired.boolean = True
    is_expired.short_description = 'Истёк?'

    def time_remaining(self, obj):
        if obj.is_expired():
            return "Истекло"
        remaining = obj.expires_at - timezone.now()
        return f"{remaining.days}д {remaining.seconds//3600}ч"
    time_remaining.short_description = 'Осталось'

    fieldsets = (
        ('Основное', {
            'fields': ('email', 'code')
        }),
        ('Даты', {
            'fields': ('created_at', 'expires_at', 'is_expired', 'time_remaining'),
            'classes': ('collapse',)
        }),
    )

    actions = ['delete_expired']

    @admin.action(description='Удалить истёкшие записи')
    def delete_expired(self, request, queryset):
        expired_count = queryset.filter(expires_at__lt=timezone.now()).count()
        queryset.filter(expires_at__lt=timezone.now()).delete()
        self.message_user(request, f'Удалено {expired_count} истёкших записей')