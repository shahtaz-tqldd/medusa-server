from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    search_fields = ['email', 'phone', 'first_name', 'last_name']
    ordering = ['date_joined']
    list_display = ("email", "first_name", "last_name", "is_staff")
