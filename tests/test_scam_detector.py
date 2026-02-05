import pytest
from app.services.scam_detector import ScamDetector
from app.models.schemas import ScamIntent


def test_financial_fraud_detection():
    """Test detection of financial fraud patterns"""
    detector = ScamDetector()
    
    message = "Your bank account has been suspended. Please verify your account details immediately."
    is_scam, intents, confidence = detector.detect(message)
    
    assert is_scam is True
    assert ScamIntent.FINANCIAL_FRAUD in intents
    assert confidence > 0.3


def test_upi_scam_detection():
    """Test detection of UPI scam patterns"""
    detector = ScamDetector()
    
    message = "Send payment to myupi@paytm for refund of Rs 5000"
    is_scam, intents, confidence = detector.detect(message)
    
    assert is_scam is True
    assert ScamIntent.UPI_SCAM in intents
    assert confidence > 0.3


def test_fake_prize_detection():
    """Test detection of fake prize patterns"""
    detector = ScamDetector()
    
    message = "Congratulations! You have won a prize of $10,000. Claim your reward now!"
    is_scam, intents, confidence = detector.detect(message)
    
    assert is_scam is True
    assert ScamIntent.FAKE_PRIZE in intents
    assert confidence > 0.3


def test_phishing_detection():
    """Test detection of phishing patterns"""
    detector = ScamDetector()
    
    message = "Click this link to reset your password: http://fake-bank.com/reset"
    is_scam, intents, confidence = detector.detect(message)
    
    assert is_scam is True
    assert ScamIntent.PHISHING in intents
    assert confidence > 0.3


def test_job_scam_detection():
    """Test detection of job scam patterns"""
    detector = ScamDetector()
    
    message = "Work from home opportunity! Earn Rs 50,000 per month. Pay registration fee of Rs 2,000."
    is_scam, intents, confidence = detector.detect(message)
    
    assert is_scam is True
    assert ScamIntent.JOB_SCAM in intents
    assert confidence > 0.3


def test_no_scam_detection():
    """Test that legitimate messages are not flagged"""
    detector = ScamDetector()
    
    message = "Hello, how are you today? The weather is nice."
    is_scam, intents, confidence = detector.detect(message)
    
    # This might not be detected as scam
    assert ScamIntent.NONE in intents or not is_scam


def test_multiple_intents():
    """Test detection of multiple scam types in one message"""
    detector = ScamDetector()
    
    message = "You won a lottery! Click this link to claim and verify your bank account."
    is_scam, intents, confidence = detector.detect(message)
    
    assert is_scam is True
    assert len(intents) >= 2  # Should detect multiple intents
