from django.contrib import admin
from .models import Project, ProjectImage

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    search_fields = ['title', 'type', 'description']
    ordering = ['-created_at']
    list_display = ("title", "type", "created_at",)


@admin.register(ProjectImage)
class ProjectImageAdmin(admin.ModelAdmin):
    search_fields = ['project__title']
    ordering = ['-created_at']
    list_display = ("project__title", "created_at",)
