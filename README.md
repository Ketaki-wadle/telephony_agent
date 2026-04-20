# AI-Powered Telephony Agent

This project is a Django + Django REST Framework backend for a property voice assistant. It supports:

- property data stored in the database
- AI answers grounded in database facts
- Twilio voice webhook flow
- Vapi webhook flow
- optional conversation transcript storage
- PostgreSQL-first deployment with SQLite local fallback

## Features

- `POST /api/ask/` answers flat/property questions from DB data
- `POST /api/twilio/voice/` handles Twilio voice webhook requests
- `POST /api/vapi/webhook/` handles Vapi webhook requests
- `GET /api/properties/` lists stored properties
- `GET /api/transcripts/` lists saved call/session transcripts
- `ConversationTranscript` stores caller utterance, AI reply, session ID, and raw payload

## Data Model

The `Property` model includes:

- `id`
- `title`
- `location`
- `price`
- `carpet_area`
- `bedrooms`
- `amenities`
- `description`
- `parking_available`

## Setup

1. Create and activate a virtual environment.
2. Install dependencies:

```bash
python -m pip install -r requirements.txt
```

3. Copy `.env.example` values into a local `.env` file, or export them directly in the shell.
4. Configure PostgreSQL using the `POSTGRES_*` environment variables.
5. Run migrations and seed sample data:

```bash
python manage.py makemigrations
python manage.py migrate
python manage.py seed_properties
python manage.py runserver
```

## PostgreSQL Setup

If you want to run exactly against PostgreSQL, use the included Docker setup:

```bash
docker compose up -d
copy .env.postgres.example .env
python manage.py migrate
python manage.py seed_properties
python manage.py runserver
```

This starts a local PostgreSQL instance on `localhost:5432` and points Django to it through `.env`.

## Demo API

### Ask a question

```bash
curl -X POST http://127.0.0.1:8000/api/ask/ \
  -H "Content-Type: application/json" \
  -d "{\"property_id\":1,\"question\":\"What is the carpet area?\",\"session_id\":\"demo-1\"}"
```

### Twilio webhook

Configure your Twilio Voice webhook to point to:

- `https://<public-url>/api/twilio/voice/`

The first request returns TwiML with a speech gather prompt. The next request with `SpeechResult` returns a spoken answer based on DB facts.

Local simulated Twilio test:

```powershell
Invoke-WebRequest `
  -Uri "http://127.0.0.1:8000/api/twilio/voice/" `
  -Method Post `
  -Body "CallSid=CA111&SpeechResult=What is the carpet area?&property_id=1" `
  -ContentType "application/x-www-form-urlencoded" `
  -UseBasicParsing
```

### Vapi webhook

Configure your Vapi assistant or server tool webhook to point to:

- `https://<public-url>/api/vapi/webhook/`

Example payload:

```json
{
  "session_id": "vapi-demo-1",
  "property_id": 1,
  "message": "Is parking available?"
}
```

Local simulated Vapi test:

```powershell
Invoke-RestMethod `
  -Uri "http://127.0.0.1:8000/api/vapi/webhook/" `
  -Method Post `
  -ContentType "application/json" `
  -Body '{"session_id":"vapi-demo-1","property_id":1,"message":"Is parking available?"}'
```

### Transcripts

After running the tests above, inspect saved interactions at:

- `GET /api/transcripts/`
- Django admin -> `Conversation transcripts`

## AI Provider Modes

- `AI_PROVIDER=mock`: uses rule-based answers backed by the database
- `AI_PROVIDER=openai`: uses OpenAI with database facts in the prompt
- `AI_PROVIDER=gemini`: uses Gemini with database facts in the prompt

If the required API package or API key is missing, the service falls back to the mock provider.

## Notes

- PostgreSQL is supported through Django settings and `psycopg`.
- SQLite is used as a local fallback if PostgreSQL environment variables are not set.
- Use ngrok or a similar tunnel to expose the webhook endpoints to Twilio or Vapi during local development.
- A real Twilio or Vapi account is only needed for live voice calls. The backend telephony logic can be demonstrated locally with the included webhook simulations.
