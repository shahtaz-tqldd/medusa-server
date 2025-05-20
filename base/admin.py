from django.contrib import admin
from base.models import Visitor

@admin.register(Visitor)
class VisitorAdmin(admin.ModelAdmin):
    search_fields = ['city', 'country']
    ordering = ['-last_visit']
    list_display = ("ip_address", "country", "device_name", "last_visit")
