from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


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
    BRAZILIAN_STATES = (
        ('AC', 'Acre'), ('AL', 'Alagoas'), ('AP', 'Amapa'), ('AM', 'Amazonas'),
        ('BA', 'Bahia'), ('CE', 'Ceara'), ('DF', 'Distrito Federal'), ('ES', 'Espirito Santo'),
        ('GO', 'Goias'), ('MA', 'Maranhao'), ('MT', 'Mato Grosso'), ('MS', 'Mato Grosso do Sul'),
        ('MG', 'Minas Gerais'), ('PA', 'Para'), ('PB', 'Paraiba'), ('PR', 'Parana'),
        ('PE', 'Pernambuco'), ('PI', 'Piaui'), ('RJ', 'Rio de Janeiro'), ('RN', 'Rio Grande do Norte'),
        ('RS', 'Rio Grande do Sul'), ('RO', 'Rondonia'), ('RR', 'Roraima'), ('SC', 'Santa Catarina'),
        ('SP', 'Sao Paulo'), ('SE', 'Sergipe'), ('TO', 'Tocantins'),
    )
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='candidate_profile')
    bio = models.TextField(blank=True, help_text='Resumo profissional (20-1000 caracteres)')
    skills = models.TextField(help_text='Separe as habilidades por virgula', blank=True)
    experience = models.TextField(blank=True)
    experience_years = models.PositiveIntegerField(default=0, help_text='Anos de experiencia')
    education = models.TextField(blank=True)
    resume = models.FileField(upload_to='resumes/', blank=True, null=True)
    linkedin_url = models.URLField(blank=True)
    github_url = models.URLField(blank=True)
    portfolio_url = models.URLField(blank=True)
    desired_salary = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    location = models.CharField(max_length=100, blank=True)
    city = models.CharField(max_length=100, blank=True, verbose_name='Cidade')
    state = models.CharField(max_length=2, choices=BRAZILIAN_STATES, blank=True, verbose_name='Estado')
    age = models.PositiveIntegerField(blank=True, null=True, verbose_name='Idade')
    interest_area = models.CharField(max_length=200, blank=True, verbose_name='Area de Interesse')
    available = models.BooleanField(default=True)
    
    def __str__(self):
        return f"Perfil de {self.user.get_full_name() or self.user.username}"
    
    def get_skills_list(self):
        if self.skills:
            return [s.strip().lower() for s in self.skills.split(',') if s.strip()]
        return []
    
    def get_full_location(self):
        if self.city and self.state:
            return f"{self.city}, {self.state}"
        return self.location or self.city or ''
    
    def is_complete(self):
        required_fields = [self.bio, self.skills, self.city, self.state]
        return all(required_fields) and len(self.bio) >= 20


class CompanyProfile(models.Model):
    COMPANY_SIZE_CHOICES = (
        ('1-10', '1-10 funcionarios'),
        ('11-50', '11-50 funcionarios'),
        ('51-200', '51-200 funcionarios'),
        ('201-500', '201-500 funcionarios'),
        ('500+', 'Mais de 500 funcionarios'),
    )
    
    VERIFICATION_STATUS_CHOICES = (
        ('pending', 'Pendente'),
        ('approved', 'Aprovada'),
        ('rejected', 'Rejeitada'),
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
    cnpj = models.CharField(max_length=18, blank=True, help_text='CNPJ da empresa')
    verification_status = models.CharField(
        max_length=20, 
        choices=VERIFICATION_STATUS_CHOICES, 
        default='pending'
    )
    verification_date = models.DateTimeField(blank=True, null=True)
    verification_notes = models.TextField(blank=True, help_text='Notas sobre a verificacao')
    
    def __str__(self):
        return self.company_name
    
    def is_verified(self):
        return self.verification_status == 'approved'


class ProblemReport(models.Model):
    CATEGORY_CHOICES = (
        ('bug', 'Bug/Erro'),
        ('feature', 'Sugestao de Funcionalidade'),
        ('account', 'Problema com Conta'),
        ('job', 'Problema com Vaga'),
        ('match', 'Problema com Match'),
        ('chat', 'Problema com Chat'),
        ('other', 'Outro'),
    )
    
    STATUS_CHOICES = (
        ('open', 'Aberto'),
        ('in_progress', 'Em Andamento'),
        ('resolved', 'Resolvido'),
        ('closed', 'Fechado'),
    )
    
    PRIORITY_CHOICES = (
        ('low', 'Baixa'),
        ('medium', 'Media'),
        ('high', 'Alta'),
        ('critical', 'Critica'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='problem_reports')
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    title = models.CharField(max_length=200)
    description = models.TextField()
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    admin_notes = models.TextField(blank=True, help_text='Notas do administrador')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    resolved_at = models.DateTimeField(blank=True, null=True)
    resolved_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='resolved_problems'
    )
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} - {self.get_status_display()}"


class SiteSettings(models.Model):
    maintenance_mode = models.BooleanField(default=False)
    maintenance_message = models.TextField(
        default='O site esta em manutencao. Voltaremos em breve!',
        blank=True
    )
    maintenance_end_time = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True
    )
    
    class Meta:
        verbose_name = 'Configuracoes do Site'
        verbose_name_plural = 'Configuracoes do Site'
    
    def __str__(self):
        return 'Configuracoes do Site'
    
    @classmethod
    def get_settings(cls):
        settings, created = cls.objects.get_or_create(pk=1)
        return settings


class SiteMetrics(models.Model):
    date = models.DateField(unique=True, default=timezone.now)
    page_views = models.PositiveIntegerField(default=0)
    unique_visitors = models.PositiveIntegerField(default=0)
    new_users = models.PositiveIntegerField(default=0)
    new_companies = models.PositiveIntegerField(default=0)
    new_jobs = models.PositiveIntegerField(default=0)
    new_applications = models.PositiveIntegerField(default=0)
    chat_messages = models.PositiveIntegerField(default=0)
    matches_created = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['-date']
        verbose_name = 'Metricas do Site'
        verbose_name_plural = 'Metricas do Site'
    
    def __str__(self):
        return f"Metricas de {self.date}"
    
    @classmethod
    def get_today(cls):
        today = timezone.now().date()
        metrics, created = cls.objects.get_or_create(date=today)
        return metrics
    
    @classmethod
    def increment(cls, field_name, amount=1):
        metrics = cls.get_today()
        current_value = getattr(metrics, field_name, 0)
        setattr(metrics, field_name, current_value + amount)
        metrics.save()
        return metrics


class CanonicalSkill(models.Model):
    name = models.CharField(max_length=100, unique=True, help_text='Nome canonico da habilidade')
    aliases = models.TextField(blank=True, help_text='Variacoes conhecidas, separadas por virgula')
    category = models.CharField(max_length=50, blank=True, help_text='Categoria da habilidade')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['name']
        verbose_name = 'Habilidade Canonica'
        verbose_name_plural = 'Habilidades Canonicas'
    
    def __str__(self):
        return self.name
    
    def get_aliases_list(self):
        if self.aliases:
            return [a.strip().lower() for a in self.aliases.split(',') if a.strip()]
        return []


class SkillCorrectionLog(models.Model):
    original_term = models.CharField(max_length=100)
    corrected_term = models.CharField(max_length=100, blank=True)
    similarity_score = models.FloatField(default=0.0)
    was_auto_corrected = models.BooleanField(default=False)
    needs_review = models.BooleanField(default=False)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Log de Correcao de Habilidade'
        verbose_name_plural = 'Logs de Correcao de Habilidades'
    
    def __str__(self):
        return f"{self.original_term} -> {self.corrected_term or 'pendente'}"


class AuditLog(models.Model):
    ACTION_CHOICES = (
        ('create', 'Criacao'),
        ('update', 'Atualizacao'),
        ('delete', 'Exclusao'),
        ('approve', 'Aprovacao'),
        ('reject', 'Rejeicao'),
        ('maintenance_on', 'Manutencao Ativada'),
        ('maintenance_off', 'Manutencao Desativada'),
        ('login', 'Login'),
        ('logout', 'Logout'),
        ('status_change', 'Mudanca de Status'),
    )
    
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='audit_logs')
    action = models.CharField(max_length=30, choices=ACTION_CHOICES)
    model_name = models.CharField(max_length=100)
    object_id = models.CharField(max_length=50, blank=True)
    object_repr = models.CharField(max_length=255, blank=True)
    details = models.JSONField(default=dict, blank=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Log de Auditoria'
        verbose_name_plural = 'Logs de Auditoria'
    
    def __str__(self):
        return f"{self.user} - {self.get_action_display()} - {self.model_name}"
    
    @classmethod
    def log_action(cls, user, action, model_name, object_id='', object_repr='', details=None, ip_address=None):
        return cls.objects.create(
            user=user,
            action=action,
            model_name=model_name,
            object_id=str(object_id) if object_id else '',
            object_repr=object_repr[:255] if object_repr else '',
            details=details or {},
            ip_address=ip_address
        )


class Notification(models.Model):
    TYPE_CHOICES = (
        ('application_status', 'Status da Candidatura'),
        ('company_approved', 'Empresa Aprovada'),
        ('company_rejected', 'Empresa Rejeitada'),
        ('new_application', 'Nova Candidatura'),
        ('new_message', 'Nova Mensagem'),
        ('system', 'Sistema'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=30, choices=TYPE_CHOICES)
    title = models.CharField(max_length=200)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    link = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Notificacao'
        verbose_name_plural = 'Notificacoes'
    
    def __str__(self):
        return f"{self.title} - {self.user.username}"
    
    @classmethod
    def notify_user(cls, user, notification_type, title, message, link=''):
        return cls.objects.create(
            user=user,
            notification_type=notification_type,
            title=title,
            message=message,
            link=link
        )
