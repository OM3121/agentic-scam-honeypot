import random
from typing import List
from app.models.schemas import ScamIntent


class ReplyGenerator:
    """Generate human-like replies to engage scammers"""
    
    # Context-aware response templates
    INITIAL_RESPONSES = [
        "Hello! Thanks for reaching out. What is this about?",
        "Hi there! I got your message. Can you tell me more?",
        "Hey! I'm interested. Please explain more.",
        "Hello! This sounds interesting. What do I need to do?",
    ]
    
    CURIOUS_RESPONSES = [
        "That sounds interesting. Can you provide more details?",
        "I'm not sure I understand. Can you explain further?",
        "This is new to me. How does it work exactly?",
        "Could you tell me more about this?",
    ]
    
    CAUTIOUS_RESPONSES = [
        "I want to be sure about this. What are the next steps?",
        "This seems unusual. Can you verify your identity?",
        "I need to think about this. Can you send me more information?",
        "I'm a bit confused. Can you clarify what you need from me?",
    ]
    
    FINANCIAL_RESPONSES = [
        "What payment method do you accept?",
        "How much do I need to pay?",
        "Can you send me your payment details?",
        "Is there a processing fee involved?",
        "What's your UPI ID or bank account number?",
    ]
    
    PRIZE_RESPONSES = [
        "Really? I won something? That's amazing!",
        "What prize did I win? How do I claim it?",
        "This is exciting! What do I need to do to get my prize?",
        "I didn't enter any contest. Are you sure it's me?",
    ]
    
    JOB_RESPONSES = [
        "This job sounds perfect! What are the details?",
        "I'm looking for work. What's the salary?",
        "Is this full-time or part-time? What are the requirements?",
        "When can I start? Do I need to pay anything upfront?",
    ]
    
    STALLING_RESPONSES = [
        "Let me check my account and get back to you.",
        "I need to discuss this with my family first.",
        "Can you give me some time to think about it?",
        "I'm at work right now. Can we continue this later?",
    ]
    
    ENGAGEMENT_RESPONSES = [
        "Okay, I'm ready. What should I do next?",
        "I understand. Please guide me through the process.",
        "I'm interested in proceeding. What's the next step?",
        "Sounds good. How do we move forward?",
    ]
    
    def __init__(self):
        self.response_count = 0
    
    def generate_reply(
        self,
        message: str,
        scam_intents: List[ScamIntent],
        message_count: int
    ) -> str:
        """Generate a contextual reply based on the scam type and conversation stage"""
        
        # First message - show initial interest
        if message_count == 0:
            return random.choice(self.INITIAL_RESPONSES)
        
        # Early conversation (1-3 messages) - show curiosity
        if message_count <= 3:
            # Intent-specific responses
            if ScamIntent.FAKE_PRIZE in scam_intents:
                return random.choice(self.PRIZE_RESPONSES)
            elif ScamIntent.JOB_SCAM in scam_intents:
                return random.choice(self.JOB_RESPONSES)
            else:
                return random.choice(self.CURIOUS_RESPONSES)
        
        # Mid conversation (4-8 messages) - probe for details
        if message_count <= 8:
            # Try to extract financial details
            if any(intent in scam_intents for intent in [
                ScamIntent.FINANCIAL_FRAUD,
                ScamIntent.UPI_SCAM,
                ScamIntent.FAKE_PRIZE
            ]):
                if random.random() < 0.6:  # 60% chance
                    return random.choice(self.FINANCIAL_RESPONSES)
            
            # Mix of cautious and engaged responses
            if random.random() < 0.4:
                return random.choice(self.CAUTIOUS_RESPONSES)
            else:
                return random.choice(self.ENGAGEMENT_RESPONSES)
        
        # Late conversation (9+ messages) - stall and extract more info
        if message_count <= 15:
            # Continue probing or stalling
            if random.random() < 0.5:
                return random.choice(self.STALLING_RESPONSES)
            else:
                return random.choice(self.FINANCIAL_RESPONSES)
        
        # Very late - prepare to wind down
        responses = [
            "I think I need more time to consider this.",
            "Let me verify this information first.",
            "I'll get back to you after checking.",
            "This is taking longer than I expected. Can we pause?",
        ]
        return random.choice(responses)
    
    def generate_goodbye(self) -> str:
        """Generate a natural session ending"""
        endings = [
            "I need to go now. Thanks for the information.",
            "I'll think about it and let you know.",
            "Sorry, I have to leave. Talk later.",
            "I need to check this with someone. Bye for now.",
        ]
        return random.choice(endings)


# Global generator instance
reply_generator = ReplyGenerator()
