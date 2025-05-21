from django.contrib import admin
from .models import Conversation, Message

@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    search_fields = ['title', 'user__country']
    ordering = ['-created_at']
    list_display = ("title", "user__country", "created_at",)


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    search_fields = ['content']
    ordering = ['-created_at']
    list_display = ("content", "sender", "created_at",)
