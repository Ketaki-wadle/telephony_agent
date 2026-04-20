from rest_framework import serializers

from .models import Property


class PropertySerializer(serializers.ModelSerializer):
    class Meta:
        model = Property
        fields = [
            "id",
            "title",
            "location",
            "price",
            "carpet_area",
            "bedrooms",
            "amenities",
            "description",
            "parking_available",
        ]


class PropertyQuestionRequestSerializer(serializers.Serializer):
    property_id = serializers.IntegerField(required=False)
    question = serializers.CharField()
    session_id = serializers.CharField(required=False, allow_blank=True)


class PropertyQuestionResponseSerializer(serializers.Serializer):
    property_id = serializers.IntegerField()
    question = serializers.CharField()
    answer = serializers.CharField()
    provider = serializers.CharField()
    session_id = serializers.CharField()


class ConversationTranscriptSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    channel = serializers.CharField()
    session_id = serializers.CharField()
    property_id = serializers.IntegerField(source="property.id")
    property_title = serializers.CharField(source="property.title")
    caller_utterance = serializers.CharField()
    agent_reply = serializers.CharField()
    created_at = serializers.DateTimeField()
