import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.postgres.fields import ArrayField
from projects.models import Project


class Services(models.Model):
    """models to store work expertise"""
    id = models.CharField(max_length=255, default=uuid.uuid4, unique=True, editable=False, primary_key=True)
    name = models.CharField(max_length=255)
    description = models.TextField()

    featured_image = models.URLField(max_length=500, blank=True, null=True)
    featured_image_public_id = models.CharField(max_length=255, blank=True, null=True)

    features = ArrayField(
        models.CharField(max_length=255),
        blank=True,
        default=list,
        verbose_name=_("Features")
    )

    tech_stacks = ArrayField(
        models.CharField(max_length=50),
        blank=True,
        default=list,
        verbose_name=_("Tech Stacks")
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    order = models.IntegerField(unique=True, editable=True, null=True, blank=True)

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


class ProjectService(models.Model):
    """intermediate model to link projects and services with roles"""
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    service = models.ForeignKey(Services, on_delete=models.CASCADE)
    role = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.project.title} - {self.service.name} ({self.role})"


class SkillsAndIntroduction(models.Model):
    """models to store skills and introduction"""
    id = models.CharField(max_length=255, default=uuid.uuid4, unique=True, editable=False, primary_key=True)
    title = models.CharField(max_length=512)
    expertise = models.TextField()
    my_story = models.TextField()

    key_focus_areas = ArrayField(
        models.CharField(max_length=50),
        blank=True,
        default=list,
        verbose_name=_("Key Focus Areas")
    )

    language_and_frameworks = ArrayField(
        models.CharField(max_length=50),
        blank=True,
        default=list,
        verbose_name=_("Language and Frameworks")
    )

    tools_and_database = ArrayField(
        models.CharField(max_length=50),
        blank=True,
        default=list,
        verbose_name=_("Tools and Database")
    )

    other_competency = ArrayField(
        models.CharField(max_length=50),
        blank=True,
        default=list,
        verbose_name=_("Other Competencies")
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class Experience(models.Model):
    """Models to store work experiences"""
    id = models.CharField(max_length=255, default=uuid.uuid4, unique=True, editable=False, primary_key=True)
    position = models.CharField(max_length=64)
    details = models.TextField()
    
    started_at = models.DateField()
    ended_at = models.DateField(blank=True, null=True)
    
    company_name = models.CharField(max_length=64)
    company_location = models.CharField(max_length=64)
    company_website = models.CharField(max_length=255, blank=True, null=True)

    highlights = ArrayField(
        models.CharField(max_length=255),
        blank=True,
        default=list,
        verbose_name=_("Highlights")
    )
    
    key_contributions = ArrayField(
        models.CharField(max_length=512),
        blank=True,
        default=list,
        verbose_name=_("Key Contributions")
    )

    tech_stacks = ArrayField(
        models.CharField(max_length=50),
        blank=True,
        default=list,
        verbose_name=_("Tech Stacks")
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.position} at {self.company_name}"

    class Meta:
        verbose_name = _("Experience")
        verbose_name_plural = _("Experiences")
        ordering = ["-started_at"]


class Achievement(models.Model):
    """Models to store achievements and certifications"""
    id = models.CharField(max_length=255, default=uuid.uuid4, unique=True, editable=False, primary_key=True)
    title = models.CharField(max_length=255)
    subtitle = models.CharField(max_length=255)
    type = models.CharField(max_length=255)
    score = models.IntegerField(blank=True, null=True)

    icon_image = models.URLField(max_length=500, blank=True, null=True)
    icon_image_public_id = models.CharField(max_length=255, blank=True, null=True)
    
    credential_url = models.URLField(max_length=500, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    order = models.IntegerField(unique=True, editable=True, null=True, blank=True)

    def save(self, *args, **kwargs):
        if self.order is None:
            last_order = Services.objects.aggregate(models.Max('order'))['order__max']
            self.order = (last_order or 0) + 1

        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = _("Achievement")
        verbose_name_plural = _("Achievements")
        ordering = ["order"]
