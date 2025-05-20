from django.contrib import admin
from services.models import Services, Skills

@admin.register(Services)
class ServicesAdmin(admin.ModelAdmin):
    search_fields = ['name', 'description']
    ordering = ['-order']
    list_display = ("name", "order", "created_at")


@admin.register(Skills)
class SkillsAdmin(admin.ModelAdmin):
    search_fields = ['name', 'description']
    ordering = ['-order']
    list_display = ("name", "proficiency_level", "order", "created_at")
