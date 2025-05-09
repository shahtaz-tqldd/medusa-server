from django.contrib import admin
from .models import Projects

@admin.register(Projects)
class ProjectAdmin(admin.ModelAdmin):
    search_fields = ['name', 'type', 'description']
    ordering = ['created_at']
    list_display = ("name", "type", "created_at",)
