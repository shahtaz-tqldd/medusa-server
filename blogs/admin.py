from django.contrib import admin
from .models import Blog, Category, Tag

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    search_fields = ['name']
    ordering = ['name']
    list_display = ("name", "created_at",)

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    search_fields = ['name']
    ordering = ['name']
    list_display = ("name", "created_at",)

@admin.register(Blog)
class BlogAdmin(admin.ModelAdmin):
    search_fields = ['title', 'type', 'body']
    ordering = ['created_at']
    list_display = ("title", "category__name", "status", "created_at",)
