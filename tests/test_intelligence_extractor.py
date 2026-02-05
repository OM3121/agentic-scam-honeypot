import pytest
from app.services.intelligence_extractor import IntelligenceExtractor


def test_upi_extraction():
    """Test extraction of UPI IDs"""
    extractor = IntelligenceExtractor()
    
    message = "Send payment to myupi@paytm and backup@ybl"
    report = extractor.extract(message)
    
    assert "myupi@paytm" in report.upiIds
    assert "backup@ybl" in report.upiIds
    assert len(report.upiIds) == 2


def test_phone_extraction():
    """Test extraction of phone numbers"""
    extractor = IntelligenceExtractor()
    
    message = "Call me at 9876543210 or +91 8765432109"
    report = extractor.extract(message)
    
    assert "9876543210" in report.phoneNumbers
    assert "8765432109" in report.phoneNumbers


def test_url_extraction():
    """Test extraction of URLs"""
    extractor = IntelligenceExtractor()
    
    message = "Visit https://scam-site.com and http://phishing.net/login"
    report = extractor.extract(message)
    
    assert "https://scam-site.com" in report.urls
    assert "http://phishing.net/login" in report.urls


def test_bank_account_extraction():
    """Test extraction of bank account numbers"""
    extractor = IntelligenceExtractor()
    
    message = "Transfer to account number: 1234567890123"
    report = extractor.extract(message)
    
    assert "1234567890123" in report.bankDetails


def test_email_extraction():
    """Test extraction of email addresses"""
    extractor = IntelligenceExtractor()
    
    message = "Contact us at scammer@gmail.com for more details"
    report = extractor.extract(message)
    
    assert "scammer@gmail.com" in report.emailAddresses


def test_mixed_extraction():
    """Test extraction of multiple types of intelligence"""
    extractor = IntelligenceExtractor()
    
    message = """
    Send Rs 5000 to myupi@paytm or call 9876543210.
    Visit https://fake-bank.com or email at support@scam.com
    Account number: 9876543210123
    """
    report = extractor.extract(message)
    
    assert len(report.upiIds) >= 1
    assert len(report.phoneNumbers) >= 1
    assert len(report.urls) >= 1
    assert len(report.emailAddresses) >= 1


def test_no_extraction():
    """Test message with no extractable intelligence"""
    extractor = IntelligenceExtractor()
    
    message = "Hello, how are you doing today?"
    report = extractor.extract(message)
    
    assert len(report.upiIds) == 0
    assert len(report.phoneNumbers) == 0
    assert len(report.urls) == 0
