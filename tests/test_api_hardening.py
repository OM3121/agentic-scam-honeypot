"""
Tests for API hardening - GUVI hackathon compliance
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.config import settings

client = TestClient(app)


def test_honeypot_empty_body_returns_success():
    """Test that POST /api/honeypot with empty body returns success (not 422)"""
    response = client.post(
        "/api/honeypot",
        headers={"X-API-Key": settings.api_key},
    )
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["status"] == "success"
    assert data["reply"] == "Hello. How can I help you?"
    assert "scamDetected" not in data
    assert "confidence" not in data


def test_honeypot_null_body_returns_success():
    """Test that POST /api/honeypot with null JSON body returns success"""
    response = client.post(
        "/api/honeypot",
        headers={
            "X-API-Key": settings.api_key,
            "Content-Type": "application/json"
        },
        json=None
    )
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["status"] == "success"
    assert data["reply"] == "Hello. How can I help you?"


def test_honeypot_with_valid_payload_works():
    """Test that POST /api/honeypot with valid payload still works"""
    response = client.post(
        "/api/honeypot",
        headers={"X-API-Key": settings.api_key},
        json={
            "sessionId": "test-valid-payload",
            "message": {
                "sender": "scammer",
                "text": "Hello, you won a prize!",
                "timestamp": "2026-01-31T08:00:00.000Z"
            }
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["status"] == "success"
    assert "reply" in data
    assert isinstance(data["reply"], str)
    assert len(data["reply"]) > 0


def test_honeypot_missing_api_key_returns_401():
    """Test that POST /api/honeypot without API key returns 401"""
    response = client.post(
        "/api/honeypot",
        json={
            "sessionId": "test-session",
            "message": "test message"
        }
    )
    
    assert response.status_code == 401
    data = response.json()
    assert "detail" in data


def test_honeypot_invalid_api_key_returns_401():
    """Test that POST /api/honeypot with invalid API key returns 401"""
    response = client.post(
        "/api/honeypot",
        headers={"X-API-Key": "invalid-wrong-key"},
        json={
            "sessionId": "test-session",
            "message": "test message"
        }
    )
    
    assert response.status_code == 401
    data = response.json()
    assert "detail" in data


def test_root_endpoint_no_api_key_required():
    """Test that root endpoint does not require API key"""
    response = client.get("/")
    
    assert response.status_code == 200
    data = response.json()
    assert "message" in data


def test_health_endpoint_no_api_key_required():
    """Test that health endpoint does not require API key"""
    response = client.get("/api/v1/health")
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


def test_legacy_message_endpoint_requires_api_key():
    """Test that legacy message endpoint requires API key"""
    response = client.post(
        "/api/v1/message",
        json={
            "sessionId": "test",
            "message": "test"
        }
    )
    
    assert response.status_code == 401


def test_cleanup_endpoint_requires_api_key():
    """Test that cleanup endpoint requires API key"""
    response = client.post("/api/v1/cleanup")
    
    assert response.status_code == 401


def test_honeypot_empty_body_with_wrong_content_type():
    """Test that empty POST works even with incorrect content-type"""
    response = client.post(
        "/api/honeypot",
        headers={
            "X-API-Key": settings.api_key,
            "Content-Type": "text/plain"
        },
        content=""
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["reply"] == "Hello. How can I help you?"


def test_honeypot_response_format_compliance():
    """Test that response contains ONLY status and reply"""
    response = client.post(
        "/api/honeypot",
        headers={"X-API-Key": settings.api_key},
    )
    
    assert response.status_code == 200
    data = response.json()
    
    # Must have exactly these fields
    assert set(data.keys()) == {"status", "reply"}
    
    # Must NOT have these fields
    forbidden_fields = [
        "sessionId", "scamDetected", "scamIntents", "confidence",
        "shouldContinue", "extractedIntelligence", "metadata",
        "intelligence", "detection"
    ]
    
    for field in forbidden_fields:
        assert field not in data


def test_honeypot_multiple_empty_requests():
    """Test multiple empty POST requests in sequence"""
    for i in range(3):
        response = client.post(
            "/api/honeypot",
            headers={"X-API-Key": settings.api_key},
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["reply"] == "Hello. How can I help you?"


def test_honeypot_empty_json_object():
    """Test POST with empty JSON object {}
    
    Note: Empty JSON object {} is different from empty body.
    Empty body is accepted, but {} is missing required fields (sessionId, message)
    so it correctly returns 422 per Pydantic validation.
    """
    response = client.post(
        "/api/honeypot",
        headers={"X-API-Key": settings.api_key},
        json={}
    )
    
    # Empty JSON object should return 422 (missing required fields)
    # This is expected - we only handle completely empty/null body, not malformed JSON
    assert response.status_code == 422


def test_honeypot_get_returns_active_message():
    """Test that GET /api/honeypot returns success with active message"""
    response = client.get(
        "/api/honeypot",
        headers={"X-API-Key": settings.api_key}
    )
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["status"] == "success"
    assert data["reply"] == "Honeypot API is active"
    assert "scamDetected" not in data
    assert "confidence" not in data


def test_honeypot_get_missing_api_key_returns_401():
    """Test that GET /api/honeypot without API key returns 401"""
    response = client.get("/api/honeypot")
    
    assert response.status_code == 401
    data = response.json()
    assert "detail" in data


def test_honeypot_get_invalid_api_key_returns_401():
    """Test that GET /api/honeypot with invalid API key returns 401"""
    response = client.get(
        "/api/honeypot",
        headers={"X-API-Key": "invalid-wrong-key"}
    )
    
    assert response.status_code == 401
    data = response.json()
    assert "detail" in data


def test_honeypot_head_request():
    """Test that HEAD /api/honeypot works correctly"""
    response = client.head(
        "/api/honeypot",
        headers={"X-API-Key": settings.api_key}
    )
    
    # HEAD should return 200 with headers but no body
    assert response.status_code == 200
    # HEAD response should have no content
    assert response.content == b""
