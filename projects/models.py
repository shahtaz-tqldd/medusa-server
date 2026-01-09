import uuid

from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.utils.translation import gettext_lazy as _

from projects.choices import ProjectTypeChoices

class Project(models.Model):
    id = models.CharField(
        max_length=255, 
        default=uuid.uuid4, 
        unique=True, 
        editable=False, 
        primary_key=True
    )
    title = models.CharField(max_length=255, verbose_name=_("Title"))
    description = models.TextField(blank=True, verbose_name=_("Description"))
    case_study = models.TextField(blank=True, verbose_name=_("Case Study"))
    
    # Featured image with Cloudinary details
    featured_image_url = models.URLField(
        blank=True, 
        null=True, 
        verbose_name=_("Featured Image URL")
    )
    featured_image_public_id = models.CharField(
        max_length=255, 
        blank=True, 
        null=True,
        verbose_name=_("Featured Image Public ID")
    )

    type = models.CharField(
        max_length=20,
        choices=ProjectTypeChoices.choices,
        default=ProjectTypeChoices.OTHER,
        verbose_name=_("Project Type")
    )
    
    tech_stacks = ArrayField(
        models.CharField(max_length=50),
        blank=True,
        default=list,
        verbose_name=_("Tech Stacks")
    )
    
    features = ArrayField(
        models.CharField(max_length=255),
        blank=True,
        default=list,
        verbose_name=_("Features")
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
    
    class Meta:
        verbose_name = _("Project")
        verbose_name_plural = _("Projects")
        ordering = ["-created_at"]


class ProjectLink(models.Model):
    """Model to store project links (GitHub, Live, Demo, etc.)"""
    id = models.CharField(
        max_length=255, 
        default=uuid.uuid4, 
        unique=True, 
        editable=False, 
        primary_key=True
    )
    project = models.ForeignKey(
        Project, 
        on_delete=models.CASCADE, 
        related_name="links"
    )
    type = models.CharField(
        max_length=50, 
        verbose_name=_("Link Type"),
        help_text=_("e.g., github, live, demo, other")
    )
    label = models.CharField(
        max_length=100, 
        verbose_name=_("Link Label")
    )
    url = models.URLField(verbose_name=_("URL"))
    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.label} - {self.project.title}"
    
    class Meta:
        verbose_name = _("Project Link")
        verbose_name_plural = _("Project Links")
        ordering = ["created_at"]


class ProjectImage(models.Model):
    """Model to store project screenshot images with Cloudinary"""
    id = models.CharField(
        max_length=255, 
        default=uuid.uuid4, 
        unique=True, 
        editable=False, 
        primary_key=True
    )
    project = models.ForeignKey(
        Project, 
        on_delete=models.CASCADE, 
        related_name="images"
    )
    image_url = models.URLField(verbose_name=_("Image URL"))
    public_id = models.CharField(
        max_length=255, 
        verbose_name=_("Cloudinary Public ID")
    )
    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Image for {self.project.title}"
    
    class Meta:
        verbose_name = _("Project Image")
        verbose_name_plural = _("Project Images")
        ordering = ["created_at"]
    