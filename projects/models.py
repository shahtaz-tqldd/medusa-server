from django.db import models
from django.utils.translation import gettext_lazy as _
from projects.choices import ProjectTypeChoices


class Project(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    features = models.TextField()
    start_date = models.DateField()
    end_date = models.DateField()

    type = models.CharField(
        max_length=20,
        choices=ProjectTypeChoices.choices,
        default=ProjectTypeChoices.OTHER,
    )

    live_url = models.URLField(blank=True, null=True, verbose_name=_("Live URL"))
    github = models.URLField(blank=True, null=True, verbose_name=_("Github URL"))

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = _("Project")
        verbose_name_plural = _("Projects")
        ordering = ["-created_at"]


class ProjectImage(models.Model):
    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, related_name="images"
    )
    image = models.ImageField(upload_to="project_images/")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Image for {self.project.name}"
