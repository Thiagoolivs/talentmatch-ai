from django.db import models
from django.conf import settings


class ChatSession(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='chat_sessions')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-updated_at']
    
    def __str__(self):
        return f"Chat de {self.user.username} - {self.created_at.strftime('%d/%m/%Y %H:%M')}"


class ChatMemory(models.Model):
    """Memória persistente do assistente sobre o usuário, mantida entre sessões."""
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='chat_memory')
    content = models.TextField(blank=True, default='', help_text='Fatos duráveis sobre o usuário extraídos das conversas')
    recent_topics = models.TextField(blank=True, default='', help_text='Tópicos das conversas mais recentes')
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Memória do Chat'
        verbose_name_plural = 'Memórias do Chat'

    def __str__(self):
        return f"Memória de {self.user.username}"


class ChatMessage(models.Model):
    ROLE_CHOICES = (
        ('user', 'Usuário'),
        ('assistant', 'Assistente'),
    )
    
    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name='messages')
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['created_at']
    
    def __str__(self):
        return f"{self.role}: {self.content[:50]}..."
