from django.db import models
from django.utils.translation import gettext_lazy as _

class ProjectTypeChoices(models.TextChoices):
    WEB = "web", _("Web Development")
    SOFTWARE = "software", _("Software")
    OTHER = "other", _("Other")
