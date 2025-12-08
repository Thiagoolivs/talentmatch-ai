from django.contrib import admin
from .models import Course, Lesson, UserCourse


class LessonInline(admin.TabularInline):
    model = Lesson
    extra = 1
    ordering = ['order']


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'level', 'area', 'duration_hours', 'is_free', 'is_active', 'lesson_count')
    list_filter = ('level', 'area', 'is_free', 'is_active')
    search_fields = ('title', 'description', 'skills_taught')
    inlines = [LessonInline]
    
    def lesson_count(self, obj):
        return obj.lessons.count()
    lesson_count.short_description = 'Aulas'


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'order', 'duration_minutes')
    list_filter = ('course',)
    search_fields = ('title', 'content')
    ordering = ['course', 'order']


@admin.register(UserCourse)
class UserCourseAdmin(admin.ModelAdmin):
    list_display = ('user', 'course', 'status', 'progress', 'started_at', 'completed_at')
    list_filter = ('status', 'course__area')
    search_fields = ('user__username', 'course__title')
