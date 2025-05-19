from django.contrib import admin
from .models import Project, ProjectImage

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    search_fields = ['name', 'type', 'description']
    ordering = ['-created_at']
    list_display = ("name", "type", "created_at",)


@admin.register(ProjectImage)
class ProjectImageAdmin(admin.ModelAdmin):
    search_fields = ['project__name']
    ordering = ['-created_at']
    list_display = ("project__name", "created_at",)
