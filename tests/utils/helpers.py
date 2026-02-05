"""
Helper functions for testing hackathon API compliance
"""
from datetime import datetime, timezone


def create_hackathon_message(text: str):
    """
    Helper to create properly formatted hackathon message object
    
    Args:
        text: The message text content
        
    Returns:
        dict: Message object with sender, text, and timestamp
    """
    return {
        "sender": "scammer",
        "text": text,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
