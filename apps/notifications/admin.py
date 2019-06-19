from django.contrib import admin
from apps.accounts.models import User

from .models import Notification, NotificationUser


class AdminNotification(admin.ModelAdmin):
    model = Notification
    readonly_fields = ('viewed',)

    def save_model(self, request, obj, form, change):
        users = []
        if not 'users' in form.changed_data:
            if not 'min_age' in form.changed_data:
                min_age = 0
            else:
                min_age = form.cleaned_data.get('min_age')
            if not 'max_age' in form.changed_data:
                max_age = 2147483647
            else:
                max_age = form.cleaned_data.get('max_age')
            if not 'gender' in form.changed_data:
                gender = Notification.Gender.b.name
            else:
                gender = form.cleaned_data.get('gender')

            if 'careers' in form.changed_data:
                carrers = form.cleaned_data.get('carrers')
                users = User.objects.filter(gender=gender, carrer__in=carrers)
            elif not 'careers' in form.changed_data and 'universities' in form.changed_data:
                universities = form.cleaned_data.get('universities')
                users = User.objects.filter(gender=gender, carrer__university__in=universities)

        else:
            users = form.cleaned.get('target_users')
        obj.target_users.add(*users)
        obj.save()
        NotificationUser.objects.bulk_create([NotificationUser(user=user, push_notification=obj)] for user in users)


admin.site.register(Notification, AdminNotification)
admin.site.register(NotificationUser)
