from django.db import models
from django.utils.translation import gettext_lazy as _

class ProjectTypeChoices(models.TextChoices):
    WEB_APP = "web_app", _("Web App")
    SOFTWARE = "software", _("Software")
    OTHER = "other", _("Other")
