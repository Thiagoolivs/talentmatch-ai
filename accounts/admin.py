from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, CandidateProfile, CompanyProfile, ProblemReport, SiteSettings, SiteMetrics


class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'user_type', 'is_active', 'created_at')
    list_filter = ('user_type', 'is_active', 'is_staff')
    fieldsets = UserAdmin.fieldsets + (
        ('Informacoes Adicionais', {'fields': ('user_type', 'avatar', 'phone')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Informacoes Adicionais', {'fields': ('user_type', 'email')}),
    )


@admin.register(CandidateProfile)
class CandidateProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'location', 'experience_years', 'available', 'desired_salary')
    list_filter = ('available', 'location')
    search_fields = ('user__username', 'user__email', 'skills')


@admin.register(CompanyProfile)
class CompanyProfileAdmin(admin.ModelAdmin):
    list_display = ('company_name', 'user', 'industry', 'location', 'verification_status', 'verification_date')
    list_filter = ('verification_status', 'industry', 'size')
    search_fields = ('company_name', 'user__username', 'cnpj')
    list_editable = ('verification_status',)
    
    actions = ['approve_companies', 'reject_companies']
    
    def approve_companies(self, request, queryset):
        from django.utils import timezone
        queryset.update(verification_status='approved', verification_date=timezone.now())
        self.message_user(request, f'{queryset.count()} empresa(s) aprovada(s).')
    approve_companies.short_description = 'Aprovar empresas selecionadas'
    
    def reject_companies(self, request, queryset):
        from django.utils import timezone
        queryset.update(verification_status='rejected', verification_date=timezone.now())
        self.message_user(request, f'{queryset.count()} empresa(s) rejeitada(s).')
    reject_companies.short_description = 'Rejeitar empresas selecionadas'


@admin.register(ProblemReport)
class ProblemReportAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'category', 'priority', 'status', 'created_at', 'resolved_at')
    list_filter = ('status', 'category', 'priority')
    search_fields = ('title', 'description', 'user__username')
    list_editable = ('status', 'priority')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        (None, {'fields': ('user', 'category', 'title', 'description')}),
        ('Status', {'fields': ('status', 'priority', 'admin_notes')}),
        ('Resolucao', {'fields': ('resolved_at', 'resolved_by')}),
        ('Datas', {'fields': ('created_at', 'updated_at')}),
    )


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    list_display = ('maintenance_mode', 'updated_at', 'updated_by')
    
    def has_add_permission(self, request):
        return not SiteSettings.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(SiteMetrics)
class SiteMetricsAdmin(admin.ModelAdmin):
    list_display = ('date', 'page_views', 'unique_visitors', 'new_users', 'new_jobs', 'new_applications', 'chat_messages')
    list_filter = ('date',)
    readonly_fields = ('date', 'page_views', 'unique_visitors', 'new_users', 'new_companies', 
                       'new_jobs', 'new_applications', 'chat_messages', 'matches_created')
    
    def has_add_permission(self, request):
        return False


admin.site.register(User, CustomUserAdmin)
