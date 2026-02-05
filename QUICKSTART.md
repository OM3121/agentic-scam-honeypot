# Quick Start Guide

## Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Configure environment (optional)
cp .env.example .env
# Edit .env to set your API_KEY and other settings
```

## Running the Server

```bash
# Start the server
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

## API Documentation

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Quick Test

### Hackathon Endpoint (For Evaluation)

```bash
# Test with a scam message - returns only status and reply
curl -X POST http://localhost:8000/api/honeypot \
  -H "X-API-Key: default-api-key-change-me" \
  -H "Content-Type: application/json" \
  -d '{
    "sessionId": "test-001",
    "message": "Congratulations! You won Rs 50,000. Send UPI to winner@paytm",
    "conversationHistory": [],
    "metadata": {}
  }'
```

Response:
```json
{
  "status": "success",
  "reply": "Really? I won something? That's amazing!"
}
```

### Legacy Testing Endpoint (For Debugging)

```bash
# Test with detailed response (includes scam detection data)
curl -X POST http://localhost:8000/api/v1/message \
  -H "X-API-Key: default-api-key-change-me" \
  -H "Content-Type: application/json" \
  -d '{
    "sessionId": "test-001",
    "message": "Congratulations! You won Rs 50,000. Send UPI to winner@paytm"
  }'
```

### Using the Demo Script

```bash
# Run comprehensive demo
python demo.py
```

## Key Endpoints

### Hackathon Evaluation
- `POST /api/honeypot` - Primary submission endpoint (returns only status + reply)

### Legacy/Internal Testing
- `POST /api/v1/message` - Detailed response with scam detection data
- `GET /api/v1/health` - Check API health
- `POST /api/v1/cleanup` - Cleanup expired sessions (requires API key)

## Running Tests

```bash
# Install test dependencies
pip install pytest

# Run all tests (51 tests)
pytest tests/ -v

# Run only integration tests
pytest tests/test_hackathon_integration.py -v

# Run with coverage
pytest tests/ --cov=app
```

## Hackathon Compliance Features

1. **Simplified API Response** - Hackathon endpoint returns ONLY:
   ```json
   {
     "status": "success",
     "reply": "agent response text"
   }
   ```

2. **Internal Intelligence Extraction**:
   - UPI IDs
   - Phone numbers
   - URLs/Phishing links
   - Bank account numbers
   - Email addresses
   - Suspicious keywords

3. **Mandatory Final Callback** - Automatically sent to:
   ```
   https://hackathon.guvi.in/api/updateHoneyPotFinalResult
   ```
   
   When:
   - Scam is detected
   - Minimum engagement threshold met (3+ messages)
   - Session terminates

4. **Scam Detection** - Multiple scam types detected:
   - Financial fraud
   - Phishing
   - UPI scams
   - Fake prizes
   - Job scams
   - Romance scams
   - Tech support scams

5. **Session Management**:
   - In-memory session tracking
   - Automatic expiration
   - Conversation history

6. **Human-like Replies**:
   - Context-aware responses
   - Natural engagement
   - Progressive interaction

## Configuration Options

Edit `.env` file:

```env
# API Authentication
API_KEY=your-secret-key

# Session Limits
MAX_MESSAGES_PER_SESSION=20
MIN_MESSAGES_FOR_CALLBACK=3
SESSION_TIMEOUT_SECONDS=3600

# Callback Configuration
# Note: Callback URL is hardcoded to hackathon endpoint
CALLBACK_TIMEOUT=10
```

## Callback Payload Structure

When a session completes with detected scam activity, this payload is sent:

```json
{
  "sessionId": "session-123",
  "scamDetected": true,
  "totalMessagesExchanged": 15,
  "extractedIntelligence": {
    "bankAccounts": ["123456789012"],
    "upiIds": ["scammer@paytm"],
    "phishingLinks": ["http://fake-site.com"],
    "phoneNumbers": ["9876543210"],
    "suspiciousKeywords": ["urgent", "prize", "won"]
  },
  "agentNotes": "Detected fake_prize, upi_scam attempt. Engaged for 15 messages. Extracted 3 intelligence items."
}
```

## Production Deployment

For production use:

1. Change the default API key
2. Use environment variables for sensitive data
3. Configure callback URL for notifications
4. Consider adding rate limiting
5. Set up proper logging and monitoring
6. Use a production ASGI server like Gunicorn

```bash
# Example production command
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```
