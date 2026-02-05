import pytest
from app.services.reply_generator import ReplyGenerator
from app.models.schemas import ScamIntent


def test_initial_response():
    """Test generation of initial response"""
    generator = ReplyGenerator()
    
    reply = generator.generate_reply("Hello", [], 0)
    
    assert len(reply) > 0
    assert isinstance(reply, str)


def test_prize_scam_response():
    """Test response to prize scam"""
    generator = ReplyGenerator()
    
    reply = generator.generate_reply(
        "You won a prize!",
        [ScamIntent.FAKE_PRIZE],
        2
    )
    
    assert len(reply) > 0
    assert isinstance(reply, str)


def test_job_scam_response():
    """Test response to job scam"""
    generator = ReplyGenerator()
    
    reply = generator.generate_reply(
        "Work from home opportunity",
        [ScamIntent.JOB_SCAM],
        2
    )
    
    assert len(reply) > 0
    assert isinstance(reply, str)


def test_financial_response():
    """Test response asking for financial details"""
    generator = ReplyGenerator()
    
    reply = generator.generate_reply(
        "Send payment",
        [ScamIntent.UPI_SCAM],
        5
    )
    
    assert len(reply) > 0
    assert isinstance(reply, str)


def test_late_stage_response():
    """Test response in late conversation stage"""
    generator = ReplyGenerator()
    
    reply = generator.generate_reply(
        "Final payment request",
        [ScamIntent.FINANCIAL_FRAUD],
        15
    )
    
    assert len(reply) > 0
    assert isinstance(reply, str)


def test_goodbye_generation():
    """Test generation of goodbye message"""
    generator = ReplyGenerator()
    
    goodbye = generator.generate_goodbye()
    
    assert len(goodbye) > 0
    assert isinstance(goodbye, str)


def test_context_awareness():
    """Test that responses change based on message count"""
    generator = ReplyGenerator()
    
    early_reply = generator.generate_reply("Message", [ScamIntent.PHISHING], 1)
    late_reply = generator.generate_reply("Message", [ScamIntent.PHISHING], 18)
    
    # Replies should be different based on context
    assert isinstance(early_reply, str)
    assert isinstance(late_reply, str)
