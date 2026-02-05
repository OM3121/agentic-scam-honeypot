import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.config import settings
from tests.utils.helpers import create_hackathon_message

client = TestClient(app)


def test_root_endpoint():
    """Test root endpoint"""
    response = client.get("/")
    
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "version" in data


def test_health_endpoint():
    """Test health check endpoint"""
    response = client.get("/api/v1/health")
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "active_sessions" in data


def test_hackathon_endpoint_without_api_key():
    """Test hackathon endpoint without API key"""
    response = client.post(
        "/api/honeypot",
        json={
            "sessionId": "test-session",
            "message": create_hackathon_message("Hello")
        }
    )
    
    assert response.status_code == 401


def test_hackathon_endpoint_with_invalid_api_key():
    """Test hackathon endpoint with invalid API key"""
    response = client.post(
        "/api/honeypot",
        headers={"X-API-Key": "invalid-key"},
        json={
            "sessionId": "test-session",
            "message": create_hackathon_message("Hello")
        }
    )
    
    assert response.status_code == 401


def test_hackathon_endpoint_success():
    """Test hackathon endpoint with valid API key - returns only status and reply"""
    response = client.post(
        "/api/honeypot",
        headers={"X-API-Key": settings.api_key},
        json={
            "sessionId": "test-hackathon-session",
            "message": create_hackathon_message("You won a prize! Send UPI to claim@paytm"),
            "conversationHistory": [],
            "metadata": {
                "channel": "SMS",
                "language": "English",
                "locale": "IN"
            }
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    
    # Hackathon response should ONLY have status and reply
    assert "status" in data
    assert "reply" in data
    assert data["status"] == "success"
    assert isinstance(data["reply"], str)
    
    # Should NOT contain intelligence or scam detection fields
    assert "scamDetected" not in data
    assert "scamIntents" not in data
    assert "confidence" not in data
    assert "shouldContinue" not in data
    assert "extractedIntelligence" not in data
    assert "sessionId" not in data


def test_hackathon_endpoint_scam_message():
    """Test hackathon endpoint with scam message"""
    response = client.post(
        "/api/honeypot",
        headers={"X-API-Key": settings.api_key},
        json={
            "sessionId": "test-scam-hackathon",
            "message": create_hackathon_message("URGENT! Your bank account has been suspended. Verify your account details immediately")
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["status"] == "success"
    assert "reply" in data
    assert len(data["reply"]) > 0


def test_message_endpoint_without_api_key():
    """Test legacy message endpoint without API key"""
    response = client.post(
        "/api/v1/message",
        json={
            "sessionId": "test-session",
            "message": "Hello"
        }
    )
    
    assert response.status_code == 401


def test_message_endpoint_with_invalid_api_key():
    """Test legacy message endpoint with invalid API key"""
    response = client.post(
        "/api/v1/message",
        headers={"X-API-Key": "invalid-key"},
        json={
            "sessionId": "test-session",
            "message": "Hello"
        }
    )
    
    assert response.status_code == 401


def test_message_endpoint_success():
    """Test legacy message endpoint with valid API key"""
    response = client.post(
        "/api/v1/message",
        headers={"X-API-Key": settings.api_key},
        json={
            "sessionId": "test-session-api",
            "message": "You won a prize! Send UPI to claim@paytm"
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["sessionId"] == "test-session-api"
    assert "reply" in data
    assert "scamDetected" in data
    assert "scamIntents" in data
    assert "confidence" in data
    assert "shouldContinue" in data
    assert "extractedIntelligence" in data


def test_scam_detection_in_api():
    """Test that scam detection works through legacy API"""
    response = client.post(
        "/api/v1/message",
        headers={"X-API-Key": settings.api_key},
        json={
            "sessionId": "test-scam-session",
            "message": "URGENT! Your bank account has been suspended. Verify your account details immediately and click this link http://fake-bank.com"
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["scamDetected"] is True
    assert len(data["scamIntents"]) > 0
    assert data["confidence"] > 0


def test_intelligence_extraction_in_api():
    """Test intelligence extraction through legacy API"""
    response = client.post(
        "/api/v1/message",
        headers={"X-API-Key": settings.api_key},
        json={
            "sessionId": "test-intel-session",
            "message": "Send payment to winner@paytm or call 9876543210"
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    
    intel = data["extractedIntelligence"]
    assert len(intel["upiIds"]) > 0
    assert len(intel["phoneNumbers"]) > 0


def test_session_continuation():
    """Test session continuation across multiple messages"""
    session_id = "test-continuation-session"
    
    # First message
    response1 = client.post(
        "/api/v1/message",
        headers={"X-API-Key": settings.api_key},
        json={
            "sessionId": session_id,
            "message": "Hello, you won a prize!"
        }
    )
    
    assert response1.status_code == 200
    assert response1.json()["shouldContinue"] is True
    
    # Second message
    response2 = client.post(
        "/api/v1/message",
        headers={"X-API-Key": settings.api_key},
        json={
            "sessionId": session_id,
            "message": "Send your UPI ID to claim"
        }
    )
    
    assert response2.status_code == 200
    assert response2.json()["sessionId"] == session_id


def test_hackathon_session_continuation():
    """Test hackathon endpoint session continuation"""
    session_id = "test-hackathon-continuation"
    
    # First message
    response1 = client.post(
        "/api/honeypot",
        headers={"X-API-Key": settings.api_key},
        json={
            "sessionId": session_id,
            "message": create_hackathon_message("Hello, you won a prize!")
        }
    )
    
    assert response1.status_code == 200
    data1 = response1.json()
    assert data1["status"] == "success"
    assert "reply" in data1
    
    # Second message
    response2 = client.post(
        "/api/honeypot",
        headers={"X-API-Key": settings.api_key},
        json={
            "sessionId": session_id,
            "message": create_hackathon_message("Send your UPI ID to claim")
        }
    )
    
    assert response2.status_code == 200
    data2 = response2.json()
    assert data2["status"] == "success"
    assert "reply" in data2


def test_cleanup_endpoint():
    """Test cleanup endpoint"""
    response = client.post(
        "/api/v1/cleanup",
        headers={"X-API-Key": settings.api_key}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "active_sessions" in data


def test_cleanup_without_api_key():
    """Test cleanup endpoint without API key"""
    response = client.post("/api/v1/cleanup")
    
    assert response.status_code == 401


def test_hackathon_endpoint_with_string_message():
    """Test hackathon endpoint accepts plain string message format"""
    response = client.post(
        "/api/honeypot",
        headers={"X-API-Key": settings.api_key},
        json={
            "sessionId": "test-string-message",
            "message": "You won a prize! Send UPI to claim@paytm"
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    
    # Should return only status and reply
    assert "status" in data
    assert "reply" in data
    assert data["status"] == "success"
    assert isinstance(data["reply"], str)
    assert len(data["reply"]) > 0


def test_hackathon_endpoint_with_object_message():
    """Test hackathon endpoint accepts object message format"""
    response = client.post(
        "/api/honeypot",
        headers={"X-API-Key": settings.api_key},
        json={
            "sessionId": "test-object-message",
            "message": {
                "sender": "scammer",
                "text": "URGENT! Your account is suspended",
                "timestamp": "2026-01-31T08:25:00.000Z"
            }
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    
    # Should return only status and reply
    assert "status" in data
    assert "reply" in data
    assert data["status"] == "success"
    assert isinstance(data["reply"], str)
    assert len(data["reply"]) > 0
