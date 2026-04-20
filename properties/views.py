from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import render
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import (
    ConversationTranscriptSerializer,
    PropertyQuestionRequestSerializer,
    PropertyQuestionResponseSerializer,
    PropertySerializer,
)
from .services import ConversationEngine, twiml_response


def home_view(request):
    return render(
        request,
        "home.html",
        {
            "default_property_id": settings.DEFAULT_PROPERTY_ID,
            "provider": settings.AI_PROVIDER,
        },
    )


def favicon_view(request):
    return HttpResponse(status=204)


class HealthCheckView(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request):
        return Response(
            {
                "status": "ok",
                "provider": settings.AI_PROVIDER,
                "default_property_id": settings.DEFAULT_PROPERTY_ID,
            }
        )


class PropertyListView(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request):
        serializer = PropertySerializer(ConversationEngine().list_properties(), many=True)
        return Response(serializer.data)


class PropertyQuestionView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        serializer = PropertyQuestionRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        answer = ConversationEngine().answer_question(
            property_id=serializer.validated_data.get("property_id", settings.DEFAULT_PROPERTY_ID),
            question=serializer.validated_data["question"],
            session_id=serializer.validated_data.get("session_id", "api-session"),
            channel="api",
            payload=request.data,
        )
        response_serializer = PropertyQuestionResponseSerializer(answer)
        return Response(response_serializer.data, status=status.HTTP_200_OK)


class ConversationTranscriptListView(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request):
        serializer = ConversationTranscriptSerializer(
            ConversationEngine().list_transcripts(),
            many=True,
        )
        return Response(serializer.data)


class TwilioVoiceWebhookView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        speech_result = request.data.get("SpeechResult")
        call_sid = request.data.get("CallSid", "demo-call")
        property_id = int(request.data.get("property_id", settings.DEFAULT_PROPERTY_ID))

        if not speech_result:
            prompt = (
                "Welcome to the property assistant. "
                "Please ask a question about the flat after the beep."
            )
            xml = twiml_response(prompt, gather=True)
            return Response(xml, content_type="text/xml")

        answer = ConversationEngine().answer_question(
            property_id=property_id,
            question=speech_result,
            session_id=call_sid,
            channel="twilio",
            payload=request.data,
        )
        xml = twiml_response(answer["answer"], gather=False)
        return Response(xml, content_type="text/xml")


class VapiWebhookView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        payload = request.data
        message = (
            payload.get("message")
            or payload.get("transcript")
            or payload.get("text")
            or payload.get("user", {}).get("message")
        )
        property_id = int(payload.get("property_id", settings.DEFAULT_PROPERTY_ID))
        session_id = (
            payload.get("session_id")
            or payload.get("call", {}).get("id")
            or payload.get("conversation_id")
            or "vapi-session"
        )

        if not message:
            return Response(
                {"reply": "Please ask a question about the property."},
                status=status.HTTP_200_OK,
            )

        answer = ConversationEngine().answer_question(
            property_id=property_id,
            question=message,
            session_id=session_id,
            channel="vapi",
            payload=payload,
        )
        return Response(
            {
                "reply": answer["answer"],
                "property_id": property_id,
                "session_id": session_id,
                "provider": answer["provider"],
            }
        )
