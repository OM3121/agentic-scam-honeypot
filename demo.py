#!/usr/bin/env python3
"""
Example script demonstrating the Agentic Scam Honeypot API
"""
import requests
import json
import time
import os
from datetime import datetime, timezone
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configuration
API_URL = "http://localhost:8000"

# Load API key from environment - REQUIRED
API_KEY = os.getenv("API_KEY")
if not API_KEY:
    raise ValueError(
        "API_KEY environment variable is required. "
        "Please create a .env file with API_KEY=your-key "
        "or run: python generate_api_key.py"
    )

HEADERS = {
    "X-API-Key": API_KEY,
    "Content-Type": "application/json"
}


def send_message(session_id: str, text: str):
    """Send a message to the honeypot API in hackathon format"""
    response = requests.post(
        f"{API_URL}/api/honeypot",
        headers=HEADERS,
        json={
            "sessionId": session_id,
            "message": {
                "sender": "scammer",
                "text": text,
                "timestamp": datetime.now(timezone.utc).isoformat()
            },
            "conversationHistory": [],
            "metadata": {
                "channel": "SMS",
                "language": "English",
                "locale": "IN"
            }
        }
    )
    return response.json()


def print_response(response: dict):
    """Pretty print the API response"""
    print("\n" + "="*60)
    print(f"Status: {response['status']}")
    print(f"Reply: {response['reply']}")
    print("="*60)


def demo_fake_prize_scam():
    """Demonstrate fake prize scam detection"""
    print("\n\n🎯 DEMO 1: Fake Prize Scam")
    print("-" * 60)
    
    session_id = "demo-prize-scam"
    
    # Scammer's first message
    print("\n[SCAMMER]: Congratulations! You won Rs 50,000 prize!")
    response = send_message(
        session_id,
        "Congratulations! You have won a prize of Rs 50,000. "
        "Send your UPI ID to winner@paytm to claim immediately!"
    )
    print_response(response)
    time.sleep(1)
    
    # Scammer asks for payment
    print("\n[SCAMMER]: Pay Rs 500 processing fee to claim your prize")
    response = send_message(
        session_id,
        "To claim your prize, send Rs 500 processing fee to backup@ybl "
        "or call 9876543210 for assistance."
    )
    print_response(response)


def demo_phishing_scam():
    """Demonstrate phishing scam detection"""
    print("\n\n🎯 DEMO 2: Phishing Scam")
    print("-" * 60)
    
    session_id = "demo-phishing-scam"
    
    # Phishing attempt
    print("\n[SCAMMER]: Your bank account is suspended!")
    response = send_message(
        session_id,
        "URGENT! Your bank account has been suspended. "
        "Click here to verify: https://fake-bank.com/verify "
        "and update your password immediately."
    )
    print_response(response)
    time.sleep(1)
    
    # Follow-up with more details
    print("\n[SCAMMER]: Provide your account details")
    response = send_message(
        session_id,
        "Please verify your account number and update your details "
        "at the link provided. Contact support@fakesupport.com if you have issues."
    )
    print_response(response)


def demo_job_scam():
    """Demonstrate job scam detection"""
    print("\n\n🎯 DEMO 3: Job Scam")
    print("-" * 60)
    
    session_id = "demo-job-scam"
    
    # Job offer
    print("\n[SCAMMER]: Amazing work from home opportunity!")
    response = send_message(
        session_id,
        "Work from home opportunity! Earn Rs 50,000 per month. "
        "Simple data entry work. Pay registration fee of Rs 2,000 to join."
    )
    print_response(response)
    time.sleep(1)
    
    # Request payment
    print("\n[SCAMMER]: Send registration fee")
    response = send_message(
        session_id,
        "Send registration fee to jobportal@paytm or "
        "bank account 123456789012. Start earning today!"
    )
    print_response(response)


def demo_upi_scam():
    """Demonstrate UPI scam detection"""
    print("\n\n🎯 DEMO 4: UPI Refund Scam")
    print("-" * 60)
    
    session_id = "demo-upi-scam"
    
    # Refund claim
    print("\n[SCAMMER]: You have a pending refund")
    response = send_message(
        session_id,
        "You have a pending refund of Rs 10,000 from your last transaction. "
        "Send a small payment of Re 1 to refund@paytm to verify your UPI ID "
        "and receive your refund immediately."
    )
    print_response(response)


def check_health():
    """Check API health"""
    response = requests.get(f"{API_URL}/api/v1/health")
    print("\n📊 API Health Status:")
    print(json.dumps(response.json(), indent=2))


if __name__ == "__main__":
    print("="*60)
    print("   AGENTIC SCAM HONEYPOT API - DEMONSTRATION")
    print("="*60)
    
    try:
        # Check if API is running
        check_health()
        
        # Run demos
        demo_fake_prize_scam()
        demo_phishing_scam()
        demo_job_scam()
        demo_upi_scam()
        
        # Final health check
        print("\n")
        check_health()
        
        print("\n\n✅ Demo completed successfully!")
        print("Visit http://localhost:8000/docs for interactive API documentation")
        
    except requests.exceptions.ConnectionError:
        print("\n❌ Error: Cannot connect to API")
        print("Please ensure the server is running:")
        print("  python -m uvicorn app.main:app --host 0.0.0.0 --port 8000")
    except Exception as e:
        print(f"\n❌ Error: {e}")
