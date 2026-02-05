import httpx
import logging
from typing import Optional
from datetime import datetime, timezone
from app.models.schemas import SessionSummary, CallbackRequest, HackathonCallbackPayload
from app.core.config import settings
from app.services.session_manager import Session
from typing import List

logger = logging.getLogger(__name__)


class CallbackService:
    """Handle callbacks when engagement completes"""
    
    # Mandatory hackathon callback URL
    HACKATHON_CALLBACK_URL = "https://hackathon.guvi.in/api/updateHoneyPotFinalResult"
    
    async def send_callback(self, session: Session) -> bool:
        """
        Send mandatory callback to hackathon endpoint
        
        Sends callback when:
        - scamDetected == true AND
        - sufficient engagement is completed (message count threshold)
        
        Returns:
            True if callback was sent successfully, False otherwise
        """
        # Only send callback if scam was detected
        if not session.scam_intents or len(session.scam_intents) == 0:
            logger.info(f"No scam detected for session {session.session_id}. Skipping callback.")
            return False
        
        # Check if sufficient engagement
        if session.message_count < settings.min_messages_for_callback:
            logger.info(f"Insufficient engagement for session {session.session_id}. Skipping callback.")
            return False
        
        try:
            # Build hackathon callback payload
            callback_data = HackathonCallbackPayload(
                sessionId=session.session_id,
                scamDetected=True,
                totalMessagesExchanged=session.message_count,
                extractedIntelligence={
                    "bankAccounts": session.intelligence.bankDetails,
                    "upiIds": session.intelligence.upiIds,
                    "phishingLinks": session.intelligence.urls,
                    "phoneNumbers": session.intelligence.phoneNumbers,
                    "suspiciousKeywords": self._extract_keywords(session)
                },
                agentNotes=self._generate_summary(session)
            )
            
            # Send async HTTP POST request to mandatory hackathon endpoint
            async with httpx.AsyncClient(timeout=settings.callback_timeout) as client:
                response = await client.post(
                    self.HACKATHON_CALLBACK_URL,
                    json=callback_data.model_dump(),
                    headers={"Content-Type": "application/json"}
                )
                
                if response.status_code == 200:
                    logger.info(f"Hackathon callback sent successfully for session {session.session_id}")
                    return True
                else:
                    logger.error(
                        f"Hackathon callback failed for session {session.session_id}. "
                        f"Status: {response.status_code}, Response: {response.text}"
                    )
                    return False
                    
        except httpx.TimeoutException:
            logger.error(f"Hackathon callback timeout for session {session.session_id}")
            return False
        except Exception as e:
            logger.error(f"Hackathon callback error for session {session.session_id}: {str(e)}")
            return False
    
    def _extract_keywords(self, session: Session) -> List[str]:
        """Extract suspicious keywords from conversation"""
        keywords = []
        suspicious_terms = [
            "urgent", "prize", "won", "lottery", "claim", "verify", "account",
            "suspended", "blocked", "bank", "upi", "transfer", "payment"
        ]
        
        for msg in session.conversation_history:
            content_lower = msg.get("content", "").lower()
            for term in suspicious_terms:
                if term in content_lower and term not in keywords:
                    keywords.append(term)
        
        return keywords[:10]  # Limit to top 10
    
    def _generate_summary(self, session: Session) -> str:
        """Generate short summary for agentNotes"""
        intents = [intent.value for intent in session.scam_intents]
        intent_str = ", ".join(intents) if intents else "generic scam"
        
        intel_count = (
            len(session.intelligence.upiIds) +
            len(session.intelligence.phoneNumbers) +
            len(session.intelligence.urls) +
            len(session.intelligence.bankDetails)
        )
        
        return (
            f"Detected {intent_str} attempt. "
            f"Engaged for {session.message_count} messages. "
            f"Extracted {intel_count} intelligence items."
        )
    
    def log_summary(self, session: Session):
        """Log session summary to console"""
        logger.info(f"=== Session Summary: {session.session_id} ===")
        logger.info(f"Message Count: {session.message_count}")
        logger.info(f"Scam Intents: {[intent.value for intent in session.scam_intents]}")
        logger.info(f"Confidence: {session.get_average_confidence():.2f}")
        logger.info(f"Duration: {session.get_duration():.2f}s")
        logger.info(f"UPI IDs: {session.intelligence.upiIds}")
        logger.info(f"Phone Numbers: {session.intelligence.phoneNumbers}")
        logger.info(f"URLs: {session.intelligence.urls}")
        logger.info(f"Termination Reason: {session.termination_reason}")


# Global callback service instance
callback_service = CallbackService()
