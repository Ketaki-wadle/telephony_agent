from django.db import models


class Property(models.Model):
    title = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=12, decimal_places=2)
    carpet_area = models.PositiveIntegerField(help_text="Area in sq.ft")
    bedrooms = models.PositiveIntegerField()
    amenities = models.JSONField(default=list, blank=True)
    description = models.TextField(blank=True)
    parking_available = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"{self.title} - {self.location}"


class ConversationTranscript(models.Model):
    channel = models.CharField(max_length=32, default="api")
    session_id = models.CharField(max_length=255, db_index=True)
    property = models.ForeignKey(
        Property,
        on_delete=models.CASCADE,
        related_name="transcripts",
    )
    caller_utterance = models.TextField()
    agent_reply = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    raw_payload = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.channel}:{self.session_id}"
