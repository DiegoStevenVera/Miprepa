from django.contrib import admin

from .models import Course, Topic, Question


class CourseAdmin(admin.ModelAdmin):
    list_display = ['uid', 'name', ]


class TopicAdmin(admin.ModelAdmin):
    list_display = ['name', 'course', 'frequency', 'order_customize']
    ordering = ['course', 'order_customize']
    radio_fields = {"course": admin.VERTICAL}
    list_filter = ('name',)
    search_fields = ('name',)


class QuestionAdmin(admin.ModelAdmin):
    list_display = ['uid', 'text', 'topic', 'course', 'date_show', 'year_show']
    ordering = ['topic', ]
    list_filter = ('text',)
    search_fields = ('text',)

    def course(self, obj):
        return obj.topic.course

    course.short_description = 'Curso'
    course.admin_order_field = 'topic__course'


admin.site.register(Course, CourseAdmin)
admin.site.register(Topic, TopicAdmin)
admin.site.register(Question, QuestionAdmin)
