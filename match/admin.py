from django.contrib import admin
from .models import MatchResult


@admin.register(MatchResult)
class MatchResultAdmin(admin.ModelAdmin):
    list_display = ('candidate', 'job', 'score', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('candidate__username', 'job__title')
    ordering = ('-score',)
