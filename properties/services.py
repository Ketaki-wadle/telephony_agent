import json
import os
from decimal import Decimal
from xml.sax.saxutils import escape

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist

from .models import ConversationTranscript, Property


def format_price(value: Decimal) -> str:
    return f"Rs. {value:,.0f}"


def twiml_response(message: str, gather: bool = False) -> str:
    safe_message = escape(message)
    if gather:
        return (
            '<?xml version="1.0" encoding="UTF-8"?>'
            "<Response>"
            f"<Say>{safe_message}</Say>"
            '<Gather input="speech" action="/api/twilio/voice/" method="POST" speechTimeout="auto" />'
            "</Response>"
        )
    return (
        '<?xml version="1.0" encoding="UTF-8"?>'
        f"<Response><Say>{safe_message}</Say></Response>"
    )


class ConversationEngine:
    def list_properties(self):
        return Property.objects.all().order_by("id")

    def list_transcripts(self):
        return ConversationTranscript.objects.select_related("property").all()

    def answer_question(self, property_id: int, question: str, session_id: str, channel: str, payload):
        try:
            property_obj = Property.objects.get(id=property_id)
        except ObjectDoesNotExist:
            return {
                "property_id": property_id,
                "question": question,
                "answer": (
                    "I'm sorry, I couldn't find that property in the database. "
                    "Please check the property ID and try again."
                ),
                "provider": "mock",
                "session_id": session_id,
            }

        provider = settings.AI_PROVIDER

        if provider == "openai":
            answer = self._answer_with_openai(property_obj, question)
        elif provider == "gemini":
            answer = self._answer_with_gemini(property_obj, question)
        else:
            provider = "mock"
            answer = self._answer_with_mock(property_obj, question)

        ConversationTranscript.objects.create(
            channel=channel,
            session_id=session_id,
            property=property_obj,
            caller_utterance=question,
            agent_reply=answer,
            raw_payload=payload if isinstance(payload, dict) else dict(payload),
        )

        return {
            "property_id": property_obj.id,
            "question": question,
            "answer": answer,
            "provider": provider,
            "session_id": session_id,
        }

    def _answer_with_mock(self, property_obj: Property, question: str) -> str:
        text = question.lower()
        amenities = ", ".join(property_obj.amenities) if property_obj.amenities else ""

        if any(keyword in text for keyword in ["size", "area", "carpet"]):
            return (
                f"The carpet area for {property_obj.title} in {property_obj.location} "
                f"is {property_obj.carpet_area} sq.ft."
            )
        if "price" in text or "cost" in text:
            return f"The price of {property_obj.title} is {format_price(property_obj.price)}."
        if "location" in text or "where" in text:
            return f"The property is located in {property_obj.location}."
        if "parking" in text:
            if property_obj.parking_available:
                return "Yes, parking is available for this property."
            return "No, parking is not available for this property."
        if "bedroom" in text or "bhk" in text:
            return f"This property has {property_obj.bedrooms} bedrooms."
        if "amenities" in text or "facility" in text:
            if amenities:
                return f"The amenities include {amenities}."
            return "I'm sorry, I don't have amenities information for this property right now."
        if "description" in text or "about" in text:
            if property_obj.description:
                return property_obj.description
            return "I'm sorry, I don't have a description for this property right now."
        return (
            "I'm sorry, I don't have that information for this flat right now. "
            "You can ask about the price, location, carpet area, bedrooms, parking, or amenities."
        )

    def _build_prompt(self, property_obj: Property, question: str) -> str:
        property_payload = {
            "id": property_obj.id,
            "title": property_obj.title,
            "location": property_obj.location,
            "price": str(property_obj.price),
            "carpet_area": property_obj.carpet_area,
            "bedrooms": property_obj.bedrooms,
            "amenities": property_obj.amenities,
            "description": property_obj.description,
            "parking_available": property_obj.parking_available,
        }
        return (
            "You are a polite real-estate voice assistant. "
            "Answer only from the supplied property database facts. "
            "If the fact is missing, say you do not have that information right now.\n"
            f"Property data: {json.dumps(property_payload)}\n"
            f"Caller question: {question}"
        )

    def _answer_with_openai(self, property_obj: Property, question: str) -> str:
        try:
            from openai import OpenAI
        except ImportError:
            return self._answer_with_mock(property_obj, question)

        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            return self._answer_with_mock(property_obj, question)

        client = OpenAI(api_key=api_key)
        response = client.responses.create(
            model=os.getenv("OPENAI_MODEL", "gpt-4.1-mini"),
            input=self._build_prompt(property_obj, question),
        )
        return response.output_text.strip()

    def _answer_with_gemini(self, property_obj: Property, question: str) -> str:
        try:
            import google.generativeai as genai
        except ImportError:
            return self._answer_with_mock(property_obj, question)

        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            return self._answer_with_mock(property_obj, question)

        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(os.getenv("GEMINI_MODEL", "gemini-1.5-flash"))
        response = model.generate_content(self._build_prompt(property_obj, question))
        return response.text.strip()
