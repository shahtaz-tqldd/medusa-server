from django.contrib import admin
from services.models import Services, SkillsAndIntroduction, Experience, Achievement

@admin.register(Services)
class ServicesAdmin(admin.ModelAdmin):
    search_fields = ['name', 'description']
    ordering = ['-order']
    list_display = ("name", "order", "created_at")


@admin.register(SkillsAndIntroduction)
class SkillsAndIntroductionAdmin(admin.ModelAdmin):
    search_fields = ['title']
    list_display = ("id", "title", "updated_at")

@admin.register(Experience)
class ExperienceAdmin(admin.ModelAdmin):
    search_fields = ['position', 'company_name']
    ordering = ['-started_at']
    list_display = ("position", "company_name", "company_location", "started_at")

@admin.register(Achievement)
class AchievementAdmin(admin.ModelAdmin):
    search_fields = ['title', 'subtitle']
    ordering = ['-order']
    list_display = ("title", "subtitle", "score", "order")