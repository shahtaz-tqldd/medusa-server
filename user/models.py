import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser, User
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.core.validators import RegexValidator
from django.utils.timezone import now, timedelta

phone_regex = RegexValidator(
    regex=r"^\+?1?\d{6,15}$", message=_("Phone Number should start with +")
)

class CustomUser(AbstractUser):
    email = models.EmailField(
        unique=True,
        verbose_name=_("Email Address"),
        help_text=_("A valid email address is required!"),
    )

    username = models.CharField(
        unique=True,
        max_length=32,
        verbose_name=_("Username"),
        help_text=_("Unique username is required"),
        blank=True,
        null=False,
    )

    # Personal information
    first_name = models.CharField(max_length=32, verbose_name=_("First Name"))
    last_name = models.CharField(max_length=32, verbose_name=_("Last Name"))

    phone = models.CharField(
        validators=[phone_regex],
        max_length=17,
        blank=True,
        null=True,
        verbose_name=_("Phone Number"),
    )

    # Address fields
    address = models.CharField(
        max_length=100, blank=True, null=True, verbose_name=_("Address Line 1")
    )

    picture_url = models.URLField(
        blank=True, null=True, verbose_name=_("Profile Picture URL")
    )

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["email", "first_name", "last_name"]

    class Meta:
        verbose_name = _("User")
        verbose_name_plural = _("Users")
        ordering = ["-date_joined"]

    def __str__(self):
        return f"{self.username}"

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"

    def save(self, *args, **kwargs):
        if not self.username:
            self.username = self.email
        super().save(*args, **kwargs)


User = get_user_model()

class PasswordResetOTP(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    otp = models.CharField(max_length=4)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_valid(self):
        return now() < self.created_at + timedelta(minutes=10)
