from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Blogs

@admin.register(Blogs)
class BlogsAdmin(admin.ModelAdmin):
    search_fields = ['name', 'type', 'body']
    ordering = ['created_at']
    list_display = ("name", "type", "created_at",)
