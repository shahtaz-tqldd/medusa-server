from django.db import models
from django.utils.translation import gettext_lazy as _

class ProjectTypeChoices(models.TextChoices):
    FRONTEND_DEVELOPMENT = "frontend", _("Frontend Development")
    BACKEND_DEVELOPMENT = "backend", _("Backend Development")
    FULL_STACK_DEVELOPMENT = "full_stack", _("Full Stack Development")
    DEPLOYMENT = "deployment", _("Deployment Development")
    OTHER = "other", _("Other")
