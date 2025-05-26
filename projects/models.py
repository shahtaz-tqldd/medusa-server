import uuid

from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.utils.translation import gettext_lazy as _

from projects.choices import ProjectTypeChoices

class Project(models.Model):
    id = models.CharField(max_length=255, default=uuid.uuid4, unique=True, editable=False, primary_key=True)
    name = models.CharField(max_length=255)
    description = models.TextField()
    features = models.TextField()
    started_at = models.DateField()
    ended_at = models.DateField()

    type = models.CharField(
        max_length=20,
        choices=ProjectTypeChoices.choices,
        default=ProjectTypeChoices.OTHER,
    )
    tech_stacks = ArrayField(
        models.CharField(max_length=50),
        blank=True,
        default=list,
        verbose_name=_("Tech Stacks")
    )

    live_url = models.URLField(blank=True, null=True, verbose_name=_("Live URL"))
    github_url = models.URLField(blank=True, null=True, verbose_name=_("Github URL"))

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = _("Project")
        verbose_name_plural = _("Projects")
        ordering = ["-created_at"]


class ProjectImage(models.Model):
    id = models.CharField(max_length=255, default=uuid.uuid4, unique=True, editable=False, primary_key=True)
    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, related_name="images"
    )
    image = models.ImageField(upload_to="project_images/")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Image for {self.project.name}"
