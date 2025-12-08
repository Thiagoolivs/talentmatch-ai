from django.contrib import admin
from .models import Job, Application


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ('title', 'company', 'job_type', 'work_mode', 'location', 'is_active', 'created_at')
    list_filter = ('job_type', 'work_mode', 'is_active', 'created_at')
    search_fields = ('title', 'description', 'requirements')
    date_hierarchy = 'created_at'


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ('candidate', 'job', 'status', 'match_score', 'applied_at')
    list_filter = ('status', 'applied_at')
    search_fields = ('candidate__username', 'job__title')
    date_hierarchy = 'applied_at'
