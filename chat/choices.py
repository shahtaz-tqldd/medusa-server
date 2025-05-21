from django.db import models
from django.utils.translation import gettext_lazy as _

class MessageSenderChoice(models.TextChoices):
    AI = "ai", _("AI Assistance")
    VISITOR = "visitor", _("Visitor")
    ADMIN = "admin", _("Admin")
