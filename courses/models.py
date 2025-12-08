from django.db import models
from django.conf import settings


class Course(models.Model):
    LEVEL_CHOICES = (
        ('beginner', 'Iniciante'),
        ('intermediate', 'Intermediário'),
        ('advanced', 'Avançado'),
    )
    
    AREA_CHOICES = (
        ('programming', 'Programação'),
        ('data_science', 'Data Science'),
        ('design', 'Design'),
        ('marketing', 'Marketing'),
        ('management', 'Gestão'),
        ('languages', 'Idiomas'),
        ('soft_skills', 'Soft Skills'),
        ('other', 'Outros'),
    )
    
    title = models.CharField(max_length=200)
    description = models.TextField()
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES, default='beginner')
    area = models.CharField(max_length=30, choices=AREA_CHOICES, default='programming')
    duration_hours = models.PositiveIntegerField(help_text='Carga horária em horas')
    external_url = models.URLField(blank=True)
    image = models.ImageField(upload_to='course_images/', blank=True, null=True)
    skills_taught = models.TextField(help_text='Habilidades ensinadas, separadas por vírgula')
    instructor = models.CharField(max_length=100, blank=True)
    is_free = models.BooleanField(default=False)
    price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title
    
    def get_skills_list(self):
        if self.skills_taught:
            return [s.strip().lower() for s in self.skills_taught.split(',') if s.strip()]
        return []


class Lesson(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='lessons')
    title = models.CharField(max_length=200)
    content = models.TextField()
    order = models.PositiveIntegerField(default=0)
    video_url = models.URLField(blank=True, help_text='URL do video (YouTube, Vimeo, etc)')
    duration_minutes = models.PositiveIntegerField(default=0, help_text='Duracao em minutos')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['order']
    
    def __str__(self):
        return f"{self.course.title} - {self.title}"


class UserCourse(models.Model):
    STATUS_CHOICES = (
        ('not_started', 'Não Iniciado'),
        ('in_progress', 'Em Andamento'),
        ('completed', 'Concluído'),
    )
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='user_courses')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrollments')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='not_started')
    progress = models.PositiveIntegerField(default=0, help_text='Progresso em porcentagem (0-100)')
    started_at = models.DateTimeField(blank=True, null=True)
    completed_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'course']
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.course.title}"
