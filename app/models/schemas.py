from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Dict, Any, Union
from datetime import datetime, timezone
from enum import Enum


class MessageEvent(BaseModel):
    """Incoming scam message event"""
    sessionId: str = Field(..., description="Unique session identifier")
    message: str = Field(..., description="Message content from potential scammer")
    timestamp: Optional[datetime] = Field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)


class MessageContent(BaseModel):
    """Message content structure for hackathon format"""
    sender: str = Field(..., description="Message sender (e.g., 'scammer')")
    text: str = Field(..., description="Message text content")
    timestamp: str = Field(..., description="ISO-8601 timestamp")


class HackathonRequest(BaseModel):
    """Hackathon API request format"""
    sessionId: str = Field(..., description="Unique session identifier")
    message: Union[MessageContent, str] = Field(..., description="Message object with sender, text, timestamp OR plain text string")
    conversationHistory: Optional[List[Dict[str, str]]] = Field(default_factory=list)
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)
    
    @field_validator('message', mode='before')
    @classmethod
    def validate_message(cls, v):
        """Convert string message to MessageContent object if needed"""
        if isinstance(v, str):
            # Convert plain string to MessageContent object
            return MessageContent(
                sender="scammer",
                text=v,
                timestamp=datetime.now(timezone.utc).isoformat()
            )
        return v


class ScamIntent(str, Enum):
    """Types of scam intent detected"""
    FINANCIAL_FRAUD = "financial_fraud"
    PHISHING = "phishing"
    UPI_SCAM = "upi_scam"
    FAKE_PRIZE = "fake_prize"
    JOB_SCAM = "job_scam"
    ROMANCE_SCAM = "romance_scam"
    TECH_SUPPORT = "tech_support"
    NONE = "none"


class MessageResponse(BaseModel):
    """Response to a message event"""
    sessionId: str
    reply: str
    scamDetected: bool
    scamIntents: List[ScamIntent]
    confidence: float = Field(ge=0.0, le=1.0)
    shouldContinue: bool
    extractedIntelligence: Dict[str, List[str]] = Field(default_factory=dict)


class HackathonResponse(BaseModel):
    """Hackathon API response format - ONLY these fields"""
    status: str = "success"
    reply: str


class IntelligenceReport(BaseModel):
    """Intelligence extracted from scam conversation"""
    upiIds: List[str] = Field(default_factory=list)
    phoneNumbers: List[str] = Field(default_factory=list)
    urls: List[str] = Field(default_factory=list)
    bankDetails: List[str] = Field(default_factory=list)
    emailAddresses: List[str] = Field(default_factory=list)


class SessionSummary(BaseModel):
    """Final callback data when engagement completes"""
    sessionId: str
    messageCount: int
    scamIntents: List[ScamIntent]
    confidence: float
    intelligence: IntelligenceReport
    conversationHistory: List[Dict[str, str]]
    engagementDuration: float  # in seconds
    completedAt: datetime
    terminationReason: str


class CallbackRequest(BaseModel):
    """Callback payload sent when engagement completes"""
    sessionId: str
    summary: SessionSummary
    status: str = "completed"


class HackathonCallbackPayload(BaseModel):
    """Hackathon final callback payload format"""
    sessionId: str
    scamDetected: bool
    totalMessagesExchanged: int
    extractedIntelligence: Dict[str, List[str]]
    agentNotes: str
