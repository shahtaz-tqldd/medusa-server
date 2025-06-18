import uuid

from django.db import models
from django.utils import timezone

from base.choices import ProjectTypeChoices

class Visitor(models.Model):
    """Model to store unique visitor information"""
    id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False, primary_key=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    first_visit = models.DateTimeField(default=timezone.now)
    last_visit = models.DateTimeField(default=timezone.now)
    
    # Device information
    device_name = models.CharField(max_length=128, blank=True, null=True)
    device_type = models.CharField(max_length=64, blank=True, null=True)
    
    # Location information
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    country = models.CharField(max_length=64, blank=True, null=True)
    city = models.CharField(max_length=64, blank=True, null=True)
    
    # Analytics
    visit_count = models.PositiveIntegerField(default=1)
    total_time_spent = models.DurationField(default=timezone.timedelta)
    
    # Tracking cookie for anonymous visitors
    cookie_id = models.CharField(max_length=64, blank=True, null=True)
    
    class Meta:
        verbose_name = 'Visitor'
        verbose_name_plural = 'Visitors'
        indexes = [
            models.Index(fields=['ip_address']),
            models.Index(fields=['first_visit']),
        ]

    def __str__(self):
        return f"{self.ip_address} ({self.visit_count} visits)"
    
    def update_visit(self):
        """Update visitor stats on new visit"""
        self.visit_count += 1
        self.last_visit = timezone.now()
        self.save(update_fields=['visit_count', 'last_visit'])


class Client(models.Model):
    """Model to store client information"""
    id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False, primary_key=True)
    visitor = models.ForeignKey(Visitor, on_delete=models.SET_NULL, related_name='clients', null=True, blank=True)

    # contact details
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True, null=True)
    whatsapp = models.CharField(max_length=20, blank=True, null=True)
    
    # project details
    project_description = models.TextField()
    project_type = models.CharField(max_length=32, choices=ProjectTypeChoices.choices, default=ProjectTypeChoices.OTHER)
    budget = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    timeline = models.CharField(max_length=64, blank=True, null=True)
    design_required = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Client'
        verbose_name_plural = 'Clients'
        ordering = ['-created_at']
        
    def __str__(self):
        return f"{self.name} ({self.email})"
