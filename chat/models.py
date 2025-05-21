import uuid
from django.db import models
from django.utils import timezone
from chat.choices import MessageSenderChoice

class Conversation(models.Model):
    """Model to store distinct conversation"""

    id = models.CharField(max_length=255, default=uuid.uuid4, unique=True, editable=False, primary_key=True)
    user = models.ForeignKey('base.Visitor', on_delete=models.CASCADE, related_name='conversations')

    title = models.CharField(max_length=255, blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Conversation from {self.user.city}-{self.user.country}" if self.user.city and self.user.country else f"Conversation {self.id}"

    class Meta:
        verbose_name = 'Conversation'
        verbose_name_plural = 'Conversations'
        ordering = ('-created_at',)
        indexes = [
            models.Index(fields=['user', '-created_at'])
        ]


class Message(models.Model):
    """Model to store each message"""
    
    id = models.CharField(max_length=255, default=uuid.uuid4, unique=True, editable=False, primary_key=True)
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    
    sender = models.CharField(max_length=20, choices=MessageSenderChoice.choices)
    content = models.TextField()
    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender}: {self.content[:30]}"

    class Meta:
        verbose_name = 'Message'
        verbose_name_plural = 'Messages'
        ordering = ('created_at',)
        indexes = [
            models.Index(fields=['conversation', 'created_at']),
            models.Index(fields=['sender']),
        ]
