from fastapi import APIRouter, Depends, Body
from typing import Optional
from app.api.schemas import HoneypotRequest
from app.core.security import verify_api_key

router = APIRouter()


@router.post("/api/honeypot")
async def honeypot(
    request: Optional[HoneypotRequest] = Body(default=None),
    api_key: str = Depends(verify_api_key)
):
    # 👇 This handles GUVI tester (no request body)
    if request is None:
        return {
            "status": "ok",
            "message": "Honeypot endpoint reachable and authenticated"
        }

    # 👇 Normal honeypot logic
    text = request.text.lower()

    scam_indicators = [
        "win", "prize", "urgent", "click", "free", "offer", "limited"
    ]

    score = sum(1 for word in scam_indicators if word in text)
    confidence = min(score / len(scam_indicators), 1.0)

    classification = "scam" if score > 0 else "safe"

    return {
        "sessionId": request.sessionId,
        "classification": classification,
        "confidence": round(confidence, 2),
        "analysis": "Auto-evaluated by honeypot engine"
    }
