from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    USER_TYPE_CHOICES = (
        ('candidate', 'Candidato'),
        ('company', 'Empresa'),
        ('admin', 'Administrador'),
    )
    
    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES, default='candidate')
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def is_candidate(self):
        return self.user_type == 'candidate'
    
    def is_company(self):
        return self.user_type == 'company'
    
    def is_admin_user(self):
        return self.user_type == 'admin' or self.is_superuser


class CandidateProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='candidate_profile')
    bio = models.TextField(blank=True)
    skills = models.TextField(help_text='Separe as habilidades por vírgula', blank=True)
    experience = models.TextField(blank=True)
    education = models.TextField(blank=True)
    resume = models.FileField(upload_to='resumes/', blank=True, null=True)
    linkedin_url = models.URLField(blank=True)
    github_url = models.URLField(blank=True)
    portfolio_url = models.URLField(blank=True)
    desired_salary = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    location = models.CharField(max_length=100, blank=True)
    available = models.BooleanField(default=True)
    
    def __str__(self):
        return f"Perfil de {self.user.get_full_name() or self.user.username}"
    
    def get_skills_list(self):
        if self.skills:
            return [s.strip().lower() for s in self.skills.split(',') if s.strip()]
        return []


class CompanyProfile(models.Model):
    COMPANY_SIZE_CHOICES = (
        ('1-10', '1-10 funcionários'),
        ('11-50', '11-50 funcionários'),
        ('51-200', '51-200 funcionários'),
        ('201-500', '201-500 funcionários'),
        ('500+', 'Mais de 500 funcionários'),
    )
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='company_profile')
    company_name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    industry = models.CharField(max_length=100, blank=True)
    website = models.URLField(blank=True)
    location = models.CharField(max_length=100, blank=True)
    size = models.CharField(max_length=20, choices=COMPANY_SIZE_CHOICES, blank=True)
    founded_year = models.PositiveIntegerField(blank=True, null=True)
    logo = models.ImageField(upload_to='company_logos/', blank=True, null=True)
    
    def __str__(self):
        return self.company_name
