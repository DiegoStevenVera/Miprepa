from django.contrib import admin

# Register your models here.
from .models import University, KnowledgeArea


class UniversityAdmin(admin.ModelAdmin):
    model = University
    list_display = ('uid', 'name')


class KnowledgeAreaAdmin(admin.ModelAdmin):
    model = University
    list_display = ('uid', 'name')


admin.site.register(University, UniversityAdmin)
admin.site.register(KnowledgeArea, KnowledgeAreaAdmin)
