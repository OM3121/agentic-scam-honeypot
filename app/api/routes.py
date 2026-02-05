from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Request, Body
from app.models.schemas import MessageEvent, MessageResponse, ScamIntent, HackathonRequest, HackathonResponse
from app.core.security import verify_api_key
from app.services.session_manager import session_manager
from app.services.scam_detector import scam_detector
from app.services.intelligence_extractor import intelligence_extractor
from app.services.reply_generator import reply_generator
from app.services.callback_service import callback_service
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["honeypot"])


@router.api_route("/honeypot", methods=["GET", "POST", "HEAD"], response_model=HackathonResponse)
async def hackathon_honeypot(
    request_obj: Request,
    api_key: str = Depends(verify_api_key),
    request: Optional[HackathonRequest] = Body(None)
) -> HackathonResponse:
    """
    Primary hackathon submission endpoint
    
    Supports GET, POST, and HEAD methods for GUVI Honeypot Endpoint Tester compatibility.
    
    GET/HEAD behavior:
    - Returns HTTP 200 with success status and active message
    - Used by GUVI tester for endpoint validation
    
    POST behavior:
    - Accepts:
      - sessionId: Unique session identifier
      - message: Message content from potential scammer
      - conversationHistory: Previous conversation (optional)
      - metadata: Additional metadata (optional)
    - Can also accept empty POST body (for GUVI tester compatibility)
    
    Returns ONLY:
    - status: "success"
    - reply: Generated reply string
    
    Intelligence and scam detection remain INTERNAL.
    Final callback sent automatically when session completes.
    """
    
    # Handle GET/HEAD requests (for GUVI tester compatibility)
    if request_obj.method in ["GET", "HEAD"]:
        return HackathonResponse(
            status="success",
            reply="Honeypot API is active"
        )
    
    # Handle empty POST body (GUVI tester compatibility)
    if request is None:
        return HackathonResponse(
            status="success",
            reply="Hello. How can I help you?"
        )
    
    # Get or create session
    session = session_manager.get_or_create_session(request.sessionId)
    
    # Add incoming message to history
    session.add_message("scammer", request.message.text)
    
    # Detect scam intent (internal only)
    is_scam, scam_intents, confidence = scam_detector.detect(request.message.text)
    
    # Update session with detection results (internal only)
    for intent in scam_intents:
        session.add_scam_intent(intent)
    session.add_confidence_score(confidence)
    
    # Extract intelligence (internal only)
    intel_report = intelligence_extractor.extract(request.message.text)
    
    # Merge with existing intelligence (internal only)
    session.intelligence.upiIds.extend(intel_report.upiIds)
    session.intelligence.phoneNumbers.extend(intel_report.phoneNumbers)
    session.intelligence.urls.extend(intel_report.urls)
    session.intelligence.bankDetails.extend(intel_report.bankDetails)
    session.intelligence.emailAddresses.extend(intel_report.emailAddresses)
    
    # Deduplicate
    session.intelligence.upiIds = list(set(session.intelligence.upiIds))
    session.intelligence.phoneNumbers = list(set(session.intelligence.phoneNumbers))
    session.intelligence.urls = list(set(session.intelligence.urls))
    session.intelligence.bankDetails = list(set(session.intelligence.bankDetails))
    session.intelligence.emailAddresses = list(set(session.intelligence.emailAddresses))
    
    # Check if session should terminate
    should_terminate, termination_reason = session.should_terminate()
    
    # Generate reply
    if should_terminate:
        reply = reply_generator.generate_goodbye()
        session.terminate(termination_reason)
        
        # Send mandatory callback to hackathon endpoint
        await callback_service.send_callback(session)
        callback_service.log_summary(session)
        
        # Clean up session
        session_manager.delete_session(request.sessionId)
    else:
        # Generate contextual reply based on message count
        # Note: message_count includes both scammer and agent messages
        # Subtract 1 to get count of previous agent responses for reply generation
        reply = reply_generator.generate_reply(
            request.message.text,
            session.scam_intents,
            session.message_count - 1
        )
    
    # Add reply to history
    session.add_message("agent", reply)
    
    # Return ONLY status and reply (per hackathon spec)
    return HackathonResponse(
        status="success",
        reply=reply
    )

@router.post("/v1/message", response_model=MessageResponse)
async def process_message(
    event: MessageEvent,
    api_key: str = Depends(verify_api_key)
) -> MessageResponse:
    """
    Legacy endpoint - for internal testing only
    
    - Detects scam intent using rule-based logic
    - Extracts intelligence (UPI IDs, phone numbers, URLs)
    - Generates human-like reply
    - Manages session state
    - Triggers callback when engagement completes
    
    NOTE: This endpoint is NOT for hackathon evaluation.
    Use POST /api/honeypot for hackathon submissions.
    """
    
    # Get or create session
    session = session_manager.get_or_create_session(event.sessionId)
    
    # Add incoming message to history
    session.add_message("scammer", event.message)
    
    # Detect scam intent
    is_scam, scam_intents, confidence = scam_detector.detect(event.message)
    
    # Update session with detection results
    for intent in scam_intents:
        session.add_scam_intent(intent)
    session.add_confidence_score(confidence)
    
    # Extract intelligence
    intel_report = intelligence_extractor.extract(event.message)
    
    # Merge with existing intelligence
    session.intelligence.upiIds.extend(intel_report.upiIds)
    session.intelligence.phoneNumbers.extend(intel_report.phoneNumbers)
    session.intelligence.urls.extend(intel_report.urls)
    session.intelligence.bankDetails.extend(intel_report.bankDetails)
    session.intelligence.emailAddresses.extend(intel_report.emailAddresses)
    
    # Deduplicate
    session.intelligence.upiIds = list(set(session.intelligence.upiIds))
    session.intelligence.phoneNumbers = list(set(session.intelligence.phoneNumbers))
    session.intelligence.urls = list(set(session.intelligence.urls))
    session.intelligence.bankDetails = list(set(session.intelligence.bankDetails))
    session.intelligence.emailAddresses = list(set(session.intelligence.emailAddresses))
    
    # Check if session should terminate
    should_terminate, termination_reason = session.should_terminate()
    
    # Generate reply
    if should_terminate:
        reply = reply_generator.generate_goodbye()
        should_continue = False
        session.terminate(termination_reason)
        
        # Send callback
        await callback_service.send_callback(session)
        callback_service.log_summary(session)
        
        # Clean up session
        session_manager.delete_session(event.sessionId)
    else:
        reply = reply_generator.generate_reply(
            event.message,
            session.scam_intents,
            session.message_count - 1  # Exclude current message
        )
        should_continue = True
    
    # Add reply to history
    session.add_message("agent", reply)
    
    # Build response
    response = MessageResponse(
        sessionId=event.sessionId,
        reply=reply,
        scamDetected=is_scam,
        scamIntents=scam_intents if scam_intents else [ScamIntent.NONE],
        confidence=confidence,
        shouldContinue=should_continue,
        extractedIntelligence={
            "upiIds": intel_report.upiIds,
            "phoneNumbers": intel_report.phoneNumbers,
            "urls": intel_report.urls,
            "bankDetails": intel_report.bankDetails,
            "emailAddresses": intel_report.emailAddresses,
        }
    )
    
    return response

@router.get("/v1/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "active_sessions": session_manager.get_active_session_count()
    }


@router.post("/v1/cleanup")
async def cleanup_sessions(api_key: str = Depends(verify_api_key)):
    """Manually trigger cleanup of expired sessions"""
    session_manager.cleanup_expired_sessions()
    return {
        "status": "success",
        "active_sessions": session_manager.get_active_session_count()
    }
