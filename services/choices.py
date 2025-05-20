from django.db import models
from django.utils.translation import gettext_lazy as _

class ProficiencyLevel(models.IntegerChoices):
    BEGINNER = 25, _('Beginner')
    INTERMEDIATE = 50, _('Intermediate')
    ADVANCED = 75, _('Advanced')
    EXPERT = 100, _('Expert')
    