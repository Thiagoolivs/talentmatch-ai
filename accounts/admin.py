from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, CandidateProfile, CompanyProfile


class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'user_type', 'is_active', 'created_at')
    list_filter = ('user_type', 'is_active', 'is_staff')
    fieldsets = UserAdmin.fieldsets + (
        ('Informações Adicionais', {'fields': ('user_type', 'avatar', 'phone')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Informações Adicionais', {'fields': ('user_type', 'email')}),
    )


@admin.register(CandidateProfile)
class CandidateProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'location', 'available', 'desired_salary')
    list_filter = ('available', 'location')
    search_fields = ('user__username', 'user__email', 'skills')


@admin.register(CompanyProfile)
class CompanyProfileAdmin(admin.ModelAdmin):
    list_display = ('company_name', 'user', 'industry', 'location', 'size')
    list_filter = ('industry', 'size')
    search_fields = ('company_name', 'user__username')


admin.site.register(User, CustomUserAdmin)
