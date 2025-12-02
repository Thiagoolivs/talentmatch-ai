from django.db import models
from django.conf import settings


class Job(models.Model):
    JOB_TYPE_CHOICES = (
        ('full_time', 'Tempo Integral'),
        ('part_time', 'Meio Período'),
        ('contract', 'Contrato'),
        ('internship', 'Estágio'),
        ('freelance', 'Freelance'),
    )
    
    WORK_MODE_CHOICES = (
        ('onsite', 'Presencial'),
        ('remote', 'Remoto'),
        ('hybrid', 'Híbrido'),
    )
    
    company = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='jobs')
    title = models.CharField(max_length=200)
    description = models.TextField()
    requirements = models.TextField(help_text='Requisitos e habilidades necessárias')
    responsibilities = models.TextField(blank=True)
    benefits = models.TextField(blank=True)
    job_type = models.CharField(max_length=20, choices=JOB_TYPE_CHOICES, default='full_time')
    work_mode = models.CharField(max_length=20, choices=WORK_MODE_CHOICES, default='onsite')
    location = models.CharField(max_length=100)
    salary_min = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    salary_max = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    experience_years = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deadline = models.DateField(blank=True, null=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} - {self.company.company_profile.company_name}"
    
    def get_requirements_list(self):
        if self.requirements:
            return [r.strip().lower() for r in self.requirements.split(',') if r.strip()]
        return []
    
    def application_count(self):
        return self.applications.count()


class Application(models.Model):
    STATUS_CHOICES = (
        ('submitted', 'Enviado'),
        ('analyzing', 'Analisando'),
        ('preselected', 'Pré-selecionado'),
        ('rejected', 'Rejeitado'),
        ('hired', 'Contratado'),
    )
    
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='applications')
    candidate = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='applications')
    cover_letter = models.TextField(blank=True)
    resume = models.FileField(upload_to='application_resumes/', blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='submitted')
    match_score = models.FloatField(default=0.0)
    applied_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    notes = models.TextField(blank=True, help_text='Notas internas da empresa')
    
    class Meta:
        ordering = ['-applied_at']
        unique_together = ['job', 'candidate']
    
    def __str__(self):
        return f"{self.candidate.username} - {self.job.title}"
