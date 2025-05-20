import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _
from services.choices import ProficiencyLevel


class Services(models.Model):
    id = models.CharField(max_length=255, default=uuid.uuid4, unique=True, editable=False, primary_key=True)
    name = models.CharField(max_length=255)
    description = models.TextField()

    order = models.IntegerField(unique=True, editable=True, null=True, blank=True)
    started_at = models.DateField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if self.order is None:
            last_order = Services.objects.aggregate(models.Max('order'))['order__max']
            self.order = (last_order or 0) + 1

        super().save(*args, **kwargs)


    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Service")
        verbose_name_plural = _("Services")
        ordering = ["order"]


class Skills(models.Model):
    id = models.CharField(max_length=255, default=uuid.uuid4, unique=True, editable=False, primary_key=True)
    name = models.CharField(max_length=64)
    description = models.TextField(blank=True, null=True)

    proficiency_level = models.IntegerField(
        choices=ProficiencyLevel.choices,
        default=ProficiencyLevel.BEGINNER
    )
    started_at = models.DateField(blank=True, null=True)
    
    order = models.IntegerField(unique=True, editable=True, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if self.order is None:
            last_order = Skills.objects.aggregate(models.Max('order'))['order__max']
            self.order = (last_order or 0) + 1
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Skill")
        verbose_name_plural = _("Skills")
        ordering = ["order"]
