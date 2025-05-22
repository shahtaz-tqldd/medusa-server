from django.contrib import admin
from services.models import Services, Skills, Experience

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

@admin.register(Experience)
class ExperienceAdmin(admin.ModelAdmin):
    search_fields = ['position', 'company_name']
    ordering = ['-started_at']
    list_display = ("position", "company_name", "company_location", "started_at")
