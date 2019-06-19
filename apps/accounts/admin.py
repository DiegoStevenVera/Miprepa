from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import ugettext_lazy as _

from .models import User, UserUniversity


class MyUserAdmin(UserAdmin):
    fieldsets = (
        (None, {'fields': ('email', 'password', 'photo', 'is_new', 'birthday', 'gender', 'nickname')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'email',)}),
        # (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser',
        #                                'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2'),
        }),
    )
    list_display = ('id', 'uid', 'email', 'nickname', 'first_name', 'last_name', 'is_staff',)
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups',)
    search_fields = ('first_name', 'last_name', 'email',)
    ordering = ('email',)
    filter_horizontal = ('groups', 'user_permissions',)


class UserUniversityAdmin(admin.ModelAdmin):
    model = UserUniversity
    list_display = ('uid', 'user', 'desired_university', 'experience', 'follows', 'first_option')


admin.site.register(User, MyUserAdmin)
admin.site.register(UserUniversity, UserUniversityAdmin)
