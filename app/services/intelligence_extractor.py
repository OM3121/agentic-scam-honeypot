import re
from typing import List
from app.models.schemas import IntelligenceReport


class IntelligenceExtractor:
    """Extract scam intelligence from messages"""
    
    # Regex patterns for intelligence extraction
    UPI_PATTERN = r'\b([a-zA-Z0-9._-]+@[a-zA-Z]+)\b'
    PHONE_PATTERN = r'\b(?:\+91|91)?[-.\s]?([6-9]\d{9})\b'
    URL_PATTERN = r'https?://(?:www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b(?:[-a-zA-Z0-9()@:%_\+.~#?&/=]*)'
    BANK_PATTERN = r'\b(?:account|a/c|ac)(?:\s+no\.?|\s+number)?\s*:?\s*(\d{9,18})\b'
    EMAIL_PATTERN = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    
    def extract(self, message: str) -> IntelligenceReport:
        """Extract intelligence from a message"""
        report = IntelligenceReport()
        
        # Extract UPI IDs
        upi_matches = re.findall(self.UPI_PATTERN, message, re.IGNORECASE)
        report.upiIds = list(set(upi_matches))
        
        # Extract phone numbers
        phone_matches = re.findall(self.PHONE_PATTERN, message)
        report.phoneNumbers = list(set(phone_matches))
        
        # Extract URLs
        url_matches = re.findall(self.URL_PATTERN, message, re.IGNORECASE)
        report.urls = list(set(url_matches))
        
        # Extract bank account numbers
        bank_matches = re.findall(self.BANK_PATTERN, message, re.IGNORECASE)
        report.bankDetails = list(set(bank_matches))
        
        # Extract email addresses (excluding UPI IDs)
        email_matches = re.findall(self.EMAIL_PATTERN, message)
        # Filter out UPI IDs from emails
        emails = [e for e in email_matches if not self._is_upi_id(e)]
        report.emailAddresses = list(set(emails))
        
        return report
    
    def _is_upi_id(self, email: str) -> bool:
        """Check if an email-like string is a UPI ID"""
        # UPI IDs typically end with common UPI handles
        upi_handles = ['paytm', 'oksbi', 'ybl', 'apl', 'axl', 'ibl', 'icici']
        domain = email.split('@')[-1].lower()
        return any(handle in domain for handle in upi_handles)
    
    def merge_reports(self, reports: List[IntelligenceReport]) -> IntelligenceReport:
        """Merge multiple intelligence reports"""
        merged = IntelligenceReport()
        
        all_upi = []
        all_phones = []
        all_urls = []
        all_banks = []
        all_emails = []
        
        for report in reports:
            all_upi.extend(report.upiIds)
            all_phones.extend(report.phoneNumbers)
            all_urls.extend(report.urls)
            all_banks.extend(report.bankDetails)
            all_emails.extend(report.emailAddresses)
        
        merged.upiIds = list(set(all_upi))
        merged.phoneNumbers = list(set(all_phones))
        merged.urls = list(set(all_urls))
        merged.bankDetails = list(set(all_banks))
        merged.emailAddresses = list(set(all_emails))
        
        return merged


# Global extractor instance
intelligence_extractor = IntelligenceExtractor()
