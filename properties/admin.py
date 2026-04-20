from django.contrib import admin

from .models import ConversationTranscript, Property


@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "location", "price", "carpet_area", "bedrooms", "parking_available")
    search_fields = ("title", "location")


@admin.register(ConversationTranscript)
class ConversationTranscriptAdmin(admin.ModelAdmin):
    list_display = ("id", "channel", "session_id", "property", "created_at")
    search_fields = ("session_id", "caller_utterance", "agent_reply")
    list_filter = ("channel", "created_at")
