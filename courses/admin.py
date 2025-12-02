from django.contrib import admin
from .models import Course, UserCourse


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'level', 'area', 'duration_hours', 'is_free', 'is_active')
    list_filter = ('level', 'area', 'is_free', 'is_active')
    search_fields = ('title', 'description', 'skills_taught')


@admin.register(UserCourse)
class UserCourseAdmin(admin.ModelAdmin):
    list_display = ('user', 'course', 'status', 'progress', 'started_at', 'completed_at')
    list_filter = ('status', 'course__area')
    search_fields = ('user__username', 'course__title')
