from django.test import TestCase
from rest_framework.test import APIClient

from .models import Property


class PropertyQuestionTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.property = Property.objects.create(
            title="2BHK Flat",
            location="Wakad, Pune",
            price="9500000.00",
            carpet_area=750,
            bedrooms=2,
            amenities=["parking", "gym"],
            description="Close to metro and schools",
            parking_available=True,
        )

    def test_question_endpoint_returns_property_fact(self):
        response = self.client.post(
            "/api/ask/",
            {
                "property_id": self.property.id,
                "question": "What is the carpet area?",
                "session_id": "test-session",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("750", response.json()["answer"])

    def test_question_endpoint_uses_default_property_id(self):
        response = self.client.post(
            "/api/ask/",
            {
                "question": "What is the location?",
                "session_id": "default-property",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("Wakad, Pune", response.json()["answer"])

    def test_twilio_webhook_returns_twiml(self):
        response = self.client.post(
            "/api/twilio/voice/",
            {
                "CallSid": "CA123",
                "SpeechResult": "Is parking available?",
                "property_id": self.property.id,
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("parking", response.content.decode().lower())

    def test_transcripts_endpoint_returns_saved_conversations(self):
        self.client.post(
            "/api/ask/",
            {
                "property_id": self.property.id,
                "question": "What is the price?",
                "session_id": "transcript-session",
            },
            format="json",
        )

        response = self.client.get("/api/transcripts/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 1)
        self.assertEqual(response.json()[0]["session_id"], "transcript-session")
