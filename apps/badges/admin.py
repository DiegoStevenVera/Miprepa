from django.contrib import admin

# Register your models here.
from .models import Level, Badge, UserUniversityBadge


class BadgeAdmin(admin.ModelAdmin):
    model = Badge
    list_display = ('uid', 'name', 'type', 'university', 'all_universities', 'is_enabled')


class UserUniversityBadgeAdmin(admin.ModelAdmin):
    model = UserUniversityBadge
    list_display = ('uid', 'created_at', 'user_university', 'badge')


admin.site.register(Level)
admin.site.register(Badge, BadgeAdmin)
admin.site.register(UserUniversityBadge, UserUniversityBadgeAdmin)
