"""
Integration test for hackathon API compliance
Tests the complete flow of the honeypot system
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.config import settings
from app.services.session_manager import session_manager
from tests.utils.helpers import create_hackathon_message

client = TestClient(app)


def test_hackathon_complete_flow():
    """
    Test complete hackathon flow:
    1. Scam message detection
    2. Intelligence extraction
    3. Multiple message exchanges
    4. Response format compliance
    5. Session termination
    """
    session_id = "integration-test-session"
    
    # Clean up any existing session
    session_manager.delete_session(session_id)
    
    # Message 1: Initial scam message
    response1 = client.post(
        "/api/honeypot",
        headers={"X-API-Key": settings.api_key},
        json={
            "sessionId": session_id,
            "message": create_hackathon_message("Congratulations! You won Rs 50,000! Send your UPI to winner@paytm to claim."),
            "conversationHistory": [],
            "metadata": {
                "channel": "SMS",
                "language": "English",
                "locale": "IN"
            }
        }
    )
    
    assert response1.status_code == 200
    data1 = response1.json()
    
    # Verify ONLY status and reply are returned
    assert set(data1.keys()) == {"status", "reply"}
    assert data1["status"] == "success"
    assert isinstance(data1["reply"], str)
    assert len(data1["reply"]) > 0
    
    # Message 2: Follow-up with more intelligence
    response2 = client.post(
        "/api/honeypot",
        headers={"X-API-Key": settings.api_key},
        json={
            "sessionId": session_id,
            "message": create_hackathon_message("Yes, you won! Send to winner@paytm or call 9876543210 urgently!"),
            "conversationHistory": [],
            "metadata": {
                "channel": "SMS",
                "language": "English",
                "locale": "IN"
            }
        }
    )
    
    assert response2.status_code == 200
    data2 = response2.json()
    assert set(data2.keys()) == {"status", "reply"}
    assert data2["status"] == "success"
    
    # Message 3: More details
    response3 = client.post(
        "/api/honeypot",
        headers={"X-API-Key": settings.api_key},
        json={
            "sessionId": session_id,
            "message": create_hackathon_message("Click http://fake-prize.com to verify. Account: 123456789012"),
            "conversationHistory": [],
            "metadata": {
                "channel": "SMS",
                "language": "English",
                "locale": "IN"
            }
        }
    )
    
    assert response3.status_code == 200
    data3 = response3.json()
    assert set(data3.keys()) == {"status", "reply"}
    assert data3["status"] == "success"
    
    # Verify session exists and has collected intelligence
    session = session_manager.get_session(session_id)
    assert session is not None
    assert session.message_count >= 6  # 3 scammer + 3 agent messages
    assert len(session.scam_intents) > 0
    assert len(session.intelligence.upiIds) > 0
    assert len(session.intelligence.phoneNumbers) > 0
    
    # Clean up
    session_manager.delete_session(session_id)


def test_hackathon_response_format_strict():
    """Test that response NEVER contains internal fields"""
    session_id = "format-test-session"
    
    response = client.post(
        "/api/honeypot",
        headers={"X-API-Key": settings.api_key},
        json={
            "sessionId": session_id,
            "message": create_hackathon_message("URGENT! Bank account suspended! Click http://phishing.com"),
            "conversationHistory": [],
            "metadata": {
                "channel": "SMS",
                "language": "English",
                "locale": "IN",
                "test": "value"
            }
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    
    # MUST have these fields
    assert "status" in data
    assert "reply" in data
    
    # MUST NOT have these fields
    forbidden_fields = [
        "sessionId", "scamDetected", "scamIntents", "confidence",
        "shouldContinue", "extractedIntelligence", "metadata",
        "intelligence", "detection"
    ]
    
    for field in forbidden_fields:
        assert field not in data, f"Field '{field}' should not be in response"
    
    # Clean up
    session_manager.delete_session(session_id)


def test_callback_conditions():
    """
    Test that callback is sent under correct conditions:
    - Scam detected
    - Minimum engagement threshold met
    """
    # This test verifies the logic but doesn't actually send the callback
    # since we can't mock the hackathon endpoint
    
    session_id = "callback-test-session"
    session_manager.delete_session(session_id)
    
    # Send enough messages to trigger callback (min 3)
    for i in range(4):
        response = client.post(
            "/api/honeypot",
            headers={"X-API-Key": settings.api_key},
            json={
                "sessionId": session_id,
                "message": create_hackathon_message(f"Message {i}: Send to scammer@paytm call 9999999999"),
            }
        )
        assert response.status_code == 200
    
    session = session_manager.get_session(session_id)
    assert session is not None
    assert session.message_count >= settings.min_messages_for_callback
    assert len(session.scam_intents) > 0  # Scam detected
    
    # Clean up
    session_manager.delete_session(session_id)


def test_no_intelligence_leak():
    """Verify intelligence is never exposed in API responses"""
    session_id = "no-leak-test"
    
    # Send message with lots of intelligence
    response = client.post(
        "/api/honeypot",
        headers={"X-API-Key": settings.api_key},
        json={
            "sessionId": session_id,
            "message": create_hackathon_message(
                "Send payment to hacker@paytm or hacker2@ybl. "
                "Call 9876543210 or 9123456789. "
                "Visit http://phishing1.com and http://phishing2.com. "
                "Account: 123456789012 or 987654321098"
            )
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    
    # Check that the reply field doesn't contain extracted intelligence
    reply_text = data.get("reply", "")
    
    # The reply should be a natural response, not containing the raw intelligence
    assert "hacker@paytm" not in reply_text
    assert "9876543210" not in reply_text
    assert "phishing1.com" not in reply_text
    assert "123456789012" not in reply_text
    
    # Verify intelligence was collected internally
    session = session_manager.get_session(session_id)
    assert len(session.intelligence.upiIds) >= 2
    assert len(session.intelligence.phoneNumbers) >= 2
    assert len(session.intelligence.urls) >= 2
    
    # Clean up
    session_manager.delete_session(session_id)


def test_authentication_required():
    """Test that all endpoints require authentication"""
    # Without API key
    response = client.post(
        "/api/honeypot",
        json={
            "sessionId": "test",
            "message": create_hackathon_message("test message")
        }
    )
    assert response.status_code == 401
    
    # With invalid API key
    response = client.post(
        "/api/honeypot",
        headers={"X-API-Key": "wrong-key"},
        json={
            "sessionId": "test",
            "message": create_hackathon_message("test message")
        }
    )
    assert response.status_code == 401


def test_multiple_sessions_independent():
    """Test that multiple sessions are managed independently"""
    session_id_1 = "multi-session-1"
    session_id_2 = "multi-session-2"
    
    # Clean up
    session_manager.delete_session(session_id_1)
    session_manager.delete_session(session_id_2)
    
    # Create two different sessions
    response1 = client.post(
        "/api/honeypot",
        headers={"X-API-Key": settings.api_key},
        json={
            "sessionId": session_id_1,
            "message": create_hackathon_message("Prize scam message with prize@paytm")
        }
    )
    
    response2 = client.post(
        "/api/honeypot",
        headers={"X-API-Key": settings.api_key},
        json={
            "sessionId": session_id_2,
            "message": create_hackathon_message("Job scam message with job@paytm")
        }
    )
    
    assert response1.status_code == 200
    assert response2.status_code == 200
    
    # Verify sessions are independent
    session1 = session_manager.get_session(session_id_1)
    session2 = session_manager.get_session(session_id_2)
    
    assert session1 is not None
    assert session2 is not None
    assert session1.session_id != session2.session_id
    
    # Clean up
    session_manager.delete_session(session_id_1)
    session_manager.delete_session(session_id_2)
