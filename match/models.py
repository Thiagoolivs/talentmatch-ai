from django.db import models
from django.conf import settings
from jobs.models import Job


class MatchResult(models.Model):
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='match_results')
    candidate = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='match_results')
    score = models.FloatField(help_text='Score de similaridade (0-1)')
    matched_skills = models.TextField(blank=True, help_text='Habilidades correspondentes')
    missing_skills = models.TextField(blank=True, help_text='Habilidades faltantes')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-score', '-created_at']
        unique_together = ['job', 'candidate']
    
    def __str__(self):
        return f"{self.candidate.username} - {self.job.title} ({self.score:.2f})"
    
    def get_matched_skills_list(self):
        if self.matched_skills:
            return [s.strip() for s in self.matched_skills.split(',') if s.strip()]
        return []
    
    def get_missing_skills_list(self):
        if self.missing_skills:
            return [s.strip() for s in self.missing_skills.split(',') if s.strip()]
        return []
