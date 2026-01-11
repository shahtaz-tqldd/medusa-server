from django.contrib import admin
from .models import Blog, Category, Tag, ContentBlock, TextBlock

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

@admin.register(ContentBlock)
class ContentBlockAdmin(admin.ModelAdmin):
    search_fields = ['blog__title']
    ordering = ['created_at']
    list_display = ("blog__title", "block_type", "order",)

@admin.register(TextBlock)
class TextBlockAdmin(admin.ModelAdmin):
    search_fields = ['content']
    list_display = ("block__block_type",)
