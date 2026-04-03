from django.contrib import admin
from .models import Chat, Message


@admin.register(Chat)
class ChatAdmin(admin.ModelAdmin):
    list_display = ("id", "initiator", "receiver", "is_typing", "date_created")
    search_fields = ("initiator__email", "receiver__email")
    list_filter = ("is_typing", "date_created")
    readonly_fields = ("date_created", "date_updated")


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ("id", "chat", "sender", "receiver", "status", "date_created")
    search_fields = ("sender__email", "receiver__email", "content")
    list_filter = ("status", "is_read", "date_created")
    readonly_fields = ("date_created", "date_updated", "deleted_at")