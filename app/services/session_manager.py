from typing import Dict, List, Optional
from datetime import datetime, timedelta, timezone
from app.models.schemas import ScamIntent, IntelligenceReport
from app.core.config import settings


class Session:
    """Represents a conversation session with a potential scammer"""
    
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.created_at = datetime.now(timezone.utc)
        self.last_activity = datetime.now(timezone.utc)
        self.message_count = 0
        self.conversation_history: List[Dict[str, str]] = []
        self.scam_intents: List[ScamIntent] = []
        self.intelligence: IntelligenceReport = IntelligenceReport()
        self.is_active = True
        self.termination_reason: Optional[str] = None
        self.confidence_scores: List[float] = []
    
    def add_message(self, role: str, content: str):
        """Add a message to conversation history"""
        self.conversation_history.append({
            "role": role,
            "content": content,
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
        self.message_count += 1
        self.last_activity = datetime.now(timezone.utc)
    
    def add_scam_intent(self, intent: ScamIntent):
        """Add detected scam intent"""
        if intent not in self.scam_intents and intent != ScamIntent.NONE:
            self.scam_intents.append(intent)
    
    def add_confidence_score(self, score: float):
        """Track confidence scores"""
        self.confidence_scores.append(score)
    
    def get_average_confidence(self) -> float:
        """Calculate average confidence score"""
        if not self.confidence_scores:
            return 0.0
        return sum(self.confidence_scores) / len(self.confidence_scores)
    
    def get_duration(self) -> float:
        """Get session duration in seconds"""
        return (datetime.now(timezone.utc) - self.created_at).total_seconds()
    
    def is_expired(self) -> bool:
        """Check if session has expired"""
        timeout = timedelta(seconds=settings.session_timeout_seconds)
        return datetime.now(timezone.utc) - self.last_activity > timeout
    
    def should_terminate(self) -> tuple[bool, Optional[str]]:
        """Determine if session should terminate"""
        if self.message_count >= settings.max_messages_per_session:
            return True, "max_messages_reached"
        
        if self.is_expired():
            return True, "session_timeout"
        
        if not self.is_active:
            return True, self.termination_reason or "manually_terminated"
        
        return False, None
    
    def terminate(self, reason: str):
        """Terminate the session"""
        self.is_active = False
        self.termination_reason = reason


class SessionManager:
    """Manages all active sessions in memory"""
    
    def __init__(self):
        self._sessions: Dict[str, Session] = {}
    
    def create_session(self, session_id: str) -> Session:
        """Create a new session"""
        if session_id in self._sessions:
            return self._sessions[session_id]
        
        session = Session(session_id)
        self._sessions[session_id] = session
        return session
    
    def get_session(self, session_id: str) -> Optional[Session]:
        """Get an existing session"""
        return self._sessions.get(session_id)
    
    def get_or_create_session(self, session_id: str) -> Session:
        """Get existing session or create new one"""
        session = self.get_session(session_id)
        if session is None:
            session = self.create_session(session_id)
        return session
    
    def delete_session(self, session_id: str):
        """Delete a session"""
        if session_id in self._sessions:
            del self._sessions[session_id]
    
    def cleanup_expired_sessions(self):
        """Remove expired sessions"""
        expired = [
            sid for sid, session in self._sessions.items()
            if session.is_expired()
        ]
        for sid in expired:
            self.delete_session(sid)
    
    def get_active_session_count(self) -> int:
        """Get count of active sessions"""
        return len(self._sessions)


# Global session manager instance
session_manager = SessionManager()
