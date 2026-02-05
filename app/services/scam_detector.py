import re
from typing import List, Tuple
from app.models.schemas import ScamIntent


class ScamDetector:
    """Rule-based scam detection system"""
    
    # Scam keywords and patterns
    SCAM_PATTERNS = {
        ScamIntent.FINANCIAL_FRAUD: [
            r'\b(urgent|immediate|act now|limited time)\b',
            r'\b(bank account|account number|credit card|debit card)\b',
            r'\b(verify|confirm|update).*\b(account|details|information)\b',
            r'\b(suspended|blocked|locked).*\b(account|card)\b',
        ],
        ScamIntent.PHISHING: [
            r'\b(click|visit|go to).*\b(link|url|website)\b',
            r'\b(reset|recover|verify).*\b(password|credentials)\b',
            r'\b(secure|verify|confirm).*\b(identity|account)\b',
            r'\b(unusual activity|suspicious login)\b',
        ],
        ScamIntent.UPI_SCAM: [
            r'\b(upi|paytm|phonepe|google pay|gpay)\b',
            r'\b(send|transfer|payment).*\b(₹|rs|rupees)\b',
            r'\b(refund|cashback|reward)\b',
            r'\b[a-zA-Z0-9._-]+@[a-zA-Z]+\b',  # UPI ID pattern
        ],
        ScamIntent.FAKE_PRIZE: [
            r'\b(won|winner|congratulations|prize|lottery)\b',
            r'\b(claim|collect).*\b(prize|reward|gift)\b',
            r'\b(lucky|selected|chosen)\b',
            r'\b(free|complimentary).*\b(gift|voucher|coupon)\b',
        ],
        ScamIntent.JOB_SCAM: [
            r'\b(job offer|employment|work from home|part time)\b',
            r'\b(earn|make).*\b(₹|rs|rupees|money)\b',
            r'\b(registration fee|training fee|security deposit)\b',
            r'\b(high income|guaranteed income)\b',
        ],
        ScamIntent.ROMANCE_SCAM: [
            r'\b(love|romantic|relationship|dating)\b',
            r'\b(lonely|single|looking for)\b',
            r'\b(money|financial|help|emergency)\b',
            r'\b(meet|video call).*\b(fee|payment)\b',
        ],
        ScamIntent.TECH_SUPPORT: [
            r'\b(technical support|tech support|customer support)\b',
            r'\b(virus|malware|security threat)\b',
            r'\b(computer|laptop|device).*\b(infected|compromised)\b',
            r'\b(microsoft|apple|google).*\b(support|team)\b',
        ]
    }
    
    def detect(self, message: str) -> Tuple[bool, List[ScamIntent], float]:
        """
        Detect scam intent in a message
        
        Returns:
            Tuple of (is_scam, list of intents, confidence score)
        """
        message_lower = message.lower()
        detected_intents = []
        intent_scores = {}
        
        # Check each scam type
        for intent, patterns in self.SCAM_PATTERNS.items():
            matches = 0
            for pattern in patterns:
                if re.search(pattern, message_lower, re.IGNORECASE):
                    matches += 1
            
            if matches > 0:
                detected_intents.append(intent)
                # Score based on proportion of patterns matched
                intent_scores[intent] = matches / len(patterns)
        
        # Calculate overall confidence
        if not detected_intents:
            return False, [ScamIntent.NONE], 0.0
        
        # Average confidence across all detected intents
        confidence = sum(intent_scores.values()) / len(intent_scores)
        
        # Boost confidence if multiple intent types detected
        if len(detected_intents) > 1:
            confidence = min(confidence * 1.2, 1.0)
        
        is_scam = confidence > 0.3  # Lower threshold for detection
        
        return is_scam, detected_intents, confidence


# Global detector instance
scam_detector = ScamDetector()
