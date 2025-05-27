from django.contrib import admin
from base.models import Visitor, Client, VectorizedContent

@admin.register(Visitor)
class VisitorAdmin(admin.ModelAdmin):
    search_fields = ['city', 'country']
    ordering = ['-last_visit']
    list_display = ("ip_address", "country", "device_name", "last_visit")


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    search_fields = ['name', 'project_type', 'project_description']
    ordering = ['-created_at']
    list_display = ("name", "visitor__country", "project_type", "created_at")

@admin.register(VectorizedContent)
class VectorAdmin(admin.ModelAdmin):
    search_fields = ['title', 'content']
    ordering = ['-created_at']
    list_display = ("title", "collection_type", "created_at")
