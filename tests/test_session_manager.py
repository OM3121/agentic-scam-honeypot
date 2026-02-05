import pytest
from app.services.session_manager import SessionManager, Session
from app.models.schemas import ScamIntent
from app.core.config import settings


def test_create_session():
    """Test session creation"""
    manager = SessionManager()
    session = manager.create_session("test-session-1")
    
    assert session.session_id == "test-session-1"
    assert session.message_count == 0
    assert session.is_active is True


def test_get_or_create_session():
    """Test getting or creating a session"""
    manager = SessionManager()
    
    # Create new session
    session1 = manager.get_or_create_session("test-session-2")
    assert session1.session_id == "test-session-2"
    
    # Get existing session
    session2 = manager.get_or_create_session("test-session-2")
    assert session1 is session2


def test_add_message():
    """Test adding messages to session"""
    session = Session("test-session-3")
    
    session.add_message("user", "Hello")
    session.add_message("agent", "Hi there")
    
    assert session.message_count == 2
    assert len(session.conversation_history) == 2
    assert session.conversation_history[0]["role"] == "user"
    assert session.conversation_history[1]["role"] == "agent"


def test_add_scam_intent():
    """Test adding scam intents"""
    session = Session("test-session-4")
    
    session.add_scam_intent(ScamIntent.PHISHING)
    session.add_scam_intent(ScamIntent.UPI_SCAM)
    
    assert len(session.scam_intents) == 2
    assert ScamIntent.PHISHING in session.scam_intents


def test_confidence_tracking():
    """Test confidence score tracking"""
    session = Session("test-session-5")
    
    session.add_confidence_score(0.8)
    session.add_confidence_score(0.9)
    session.add_confidence_score(0.7)
    
    avg_confidence = session.get_average_confidence()
    assert abs(avg_confidence - 0.8) < 0.01  # Allow for floating point precision


def test_session_termination():
    """Test session termination conditions"""
    session = Session("test-session-6")
    
    # Add messages up to limit
    for i in range(settings.max_messages_per_session):
        session.add_message("user", f"Message {i}")
    
    should_terminate, reason = session.should_terminate()
    assert should_terminate is True
    assert reason == "max_messages_reached"


def test_manual_termination():
    """Test manual session termination"""
    session = Session("test-session-7")
    
    session.terminate("user_requested")
    
    assert session.is_active is False
    assert session.termination_reason == "user_requested"


def test_delete_session():
    """Test session deletion"""
    manager = SessionManager()
    
    manager.create_session("test-session-8")
    assert manager.get_session("test-session-8") is not None
    
    manager.delete_session("test-session-8")
    assert manager.get_session("test-session-8") is None


def test_active_session_count():
    """Test counting active sessions"""
    manager = SessionManager()
    
    initial_count = manager.get_active_session_count()
    
    manager.create_session("test-session-9")
    manager.create_session("test-session-10")
    
    assert manager.get_active_session_count() == initial_count + 2
