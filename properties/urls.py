from django.urls import path

from .views import (
    ConversationTranscriptListView,
    HealthCheckView,
    PropertyListView,
    PropertyQuestionView,
    TwilioVoiceWebhookView,
    VapiWebhookView,
)

urlpatterns = [
    path("health/", HealthCheckView.as_view(), name="health"),
    path("properties/", PropertyListView.as_view(), name="property-list"),
    path("transcripts/", ConversationTranscriptListView.as_view(), name="transcript-list"),
    path("ask/", PropertyQuestionView.as_view(), name="property-question"),
    path("twilio/voice/", TwilioVoiceWebhookView.as_view(), name="twilio-voice"),
    path("vapi/webhook/", VapiWebhookView.as_view(), name="vapi-webhook"),
]
