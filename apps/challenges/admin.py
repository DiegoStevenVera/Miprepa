from django.contrib import admin
from .models import ChallengeTimeOut, ChallengeSurvival, ChallengeTest, History


class ChallengeTimeOutAdmin(admin.ModelAdmin):
    list_display = ['uid', 'quantity_questions']


class ChallengeSurvivalAdmin(admin.ModelAdmin):
    list_display = ['uid', 'quantity_questions', 'time']


class ChallengeTestAdmin(admin.ModelAdmin):
    list_display = ['uid', 'time']


class HistoryAdmin(admin.ModelAdmin):
    list_display = ['uid', 'created_at', 'date_at', 'status', 'experience']


admin.site.register(ChallengeTimeOut, ChallengeTimeOutAdmin)
admin.site.register(ChallengeSurvival, ChallengeTimeOutAdmin)
admin.site.register(ChallengeTest, ChallengeTestAdmin)
admin.site.register(History, HistoryAdmin)
