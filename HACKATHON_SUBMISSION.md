# Hackathon Submission Document

## India AI Impact Buildathon – AI for Fraud Detection & User Safety

---

## 1. Participant Details

- **Email ID**: 2k22it56@kiot.ac.in
- **Hackathon**: India AI Impact Buildathon
- **Challenge Track**: AI for Fraud Detection & User Safety
- **Selected Problem Statement**: Agentic Honey-Pot for Scam Detection & Intelligence Extraction

---

## 2. Problem Understanding

### The Real-World Problem

Online scams targeting Indian citizens have grown substantially, particularly:

- **UPI-based scams**: Fraudsters request UPI IDs under false pretenses (fake refunds, prizes, KYC verification)
- **Bank account fraud**: Scammers solicit account numbers and OTPs through impersonation or urgency tactics
- **Phishing attacks**: Malicious links distributed via SMS and messaging apps to steal credentials or install malware

These scams result in significant financial losses and erode trust in digital payment systems.

### Limitations of Traditional Detection

Existing fraud prevention systems typically:

- **Detect and block**: Flag suspicious messages and terminate communication immediately
- **Lack intelligence**: Cannot extract actionable data (phone numbers, UPI IDs, phishing domains) for investigation
- **Miss evolving tactics**: Static pattern-matching fails when scammers adapt their language or techniques

Once a scammer is blocked, they simply move to a new number or account. Law enforcement receives minimal intelligence to pursue investigations or identify networks.

### Need for Engagement-Based Intelligence

A honeypot approach addresses these gaps by:

- **Appearing vulnerable**: The system responds naturally, encouraging scammers to continue and reveal more information
- **Extracting intelligence**: Collects UPI IDs, phone numbers, phishing links, and bank references through multi-turn engagement
- **Supporting investigations**: Structured intelligence reports enable cybercrime units to track patterns, identify repeat offenders, and disrupt scam operations

---

## 3. Proposed Solution Overview

### System Description

This solution is a **backend REST API system** that implements an agentic honeypot for scam detection and intelligence extraction. The system operates autonomously to engage potential scammers without revealing detection.

### Core Capabilities

**1. Scam Intent Detection**

The system analyzes incoming messages using rule-based pattern matching to identify scam types:
- Financial fraud (account verification requests, suspended account threats)
- UPI scams (payment requests, refund schemes)
- Phishing (credential harvesting, malicious links)
- Fake prize/lottery scams
- Job scams (work-from-home fraud)
- Romance scams
- Tech support scams

**2. Autonomous Agent Engagement**

When scam intent is detected, the agent generates human-like, context-aware replies that:
- Show curiosity or concern appropriate to the scam scenario
- Avoid accusatory language or revealing detection
- Progressively engage the scammer across multiple message turns
- Maintain conversational coherence using session history

**3. Passive Intelligence Extraction**

During engagement, the system continuously extracts:
- UPI IDs (e.g., scammer@paytm)
- Phone numbers (mobile contact information)
- URLs and phishing links
- Bank account references
- Email addresses
- Suspicious keywords and phrases

All extraction is passive—no active queries are generated to solicit specific data.

---

## 4. System Architecture

### High-Level Components

The system is **backend-only** with no frontend interface. Architecture consists of:

**API Layer**
- FastAPI-based REST endpoints
- API key authentication (X-API-Key header)
- Request validation using Pydantic models
- Primary hackathon endpoint: `/api/honeypot`

**Session Management**
- In-memory session storage (no database)
- Unique sessionId tracking for multi-turn conversations
- Automatic session expiration (configurable timeout)
- Conversation history maintained per session

**Scam Detection Service**
- Rule-based pattern matching engine
- Multi-label classification (single message may match multiple scam types)
- Confidence scoring based on pattern match density
- Intent tracking across conversation

**Intelligence Extraction Service**
- Regex-based extraction for structured data (UPI, phone, URLs, bank accounts)
- Deduplication and aggregation across messages
- Separate handling for UPI IDs vs. general email addresses

**Reply Generation Service**
- Context-aware response generation
- Stage-based progression (curiosity → interest → engagement)
- Natural language variation to avoid robotic patterns
- No mention of scam detection in replies

**Callback Reporting Service**
- Mandatory callback to hackathon evaluation endpoint
- Triggered when: (scam detected) AND (minimum engagement threshold met) AND (session terminates)
- Structured payload with intelligence and summary
- Hardcoded endpoint: `https://hackathon.guvi.in/api/updateHoneyPotFinalResult`

---

## 5. API Design & Workflow

### Request Format

**Endpoint**: `POST /api/honeypot`

**Headers**:
- `X-API-Key`: Authentication token
- `Content-Type`: application/json

**Request Body**:
```json
{
  "sessionId": "unique-session-identifier",
  "message": "message content from potential scammer",
  "conversationHistory": [],
  "metadata": {}
}
```

### Multi-Turn Conversation Handling

Each message includes a `sessionId`. The system:
1. Retrieves existing session if present, or creates new session
2. Appends message to session conversation history
3. Runs scam detection and intelligence extraction
4. Updates session state (message count, intents, confidence)
5. Generates contextual reply based on conversation stage
6. Returns simplified response to caller

Sessions persist across multiple API calls until:
- Maximum message count reached (default: 20)
- Session timeout (default: 1 hour of inactivity)
- Manual termination

### Response Format

The API returns **only** this structure (per hackathon requirements):
```json
{
  "status": "success",
  "reply": "agent response text"
}
```

**All internal data remains hidden:**
- Scam detection status
- Confidence scores
- Extracted intelligence
- Session metadata

This ensures the scammer receives no indication of detection.

### Final Callback Workflow

When a session terminates with detected scam activity:

1. System checks callback conditions:
   - `scamDetected == true`
   - Message count ≥ minimum threshold (default: 3)

2. If conditions met, callback payload is constructed:
```json
{
  "sessionId": "session-identifier",
  "scamDetected": true,
  "totalMessagesExchanged": 15,
  "extractedIntelligence": {
    "bankAccounts": ["123456789012"],
    "upiIds": ["scammer@paytm"],
    "phishingLinks": ["http://malicious-site.com"],
    "phoneNumbers": ["9876543210"],
    "suspiciousKeywords": ["urgent", "prize", "verify"]
  },
  "agentNotes": "Detected fake_prize, upi_scam attempt. Engaged for 15 messages. Extracted 3 intelligence items."
}
```

3. HTTP POST sent to hardcoded hackathon endpoint
4. Result logged (success/failure)

---

## 6. Intelligence Extraction

### Extracted Data Types

**UPI IDs**
- Format: `identifier@handle` (e.g., user123@paytm, merchant@ybl)
- Common handles: paytm, phonepe, googlepay, ybl, oksbi, apl, axl, ibl, icici
- Regex-based extraction with UPI-specific validation

**Phone Numbers**
- Indian mobile numbers (10 digits starting with 6-9)
- Handles formats with/without country code (+91, 91)
- Tolerates separators (spaces, dots, hyphens)

**Phishing Links**
- HTTP/HTTPS URLs extracted from message text
- Includes malicious domains, fake banking sites, credential harvesting pages
- No active link validation (passive extraction only)

**Bank Account References**
- Account numbers (9-18 digits)
- Patterns like "account no: 123456789012" or "a/c 123456789012"
- Does not extract card numbers (out of scope for this system)

**Email Addresses**
- Standard email format validation
- Filtered to exclude UPI IDs (which use @ but are not emails)

**Suspicious Keywords**
- Extracted from conversation context
- Terms like "urgent", "prize", "won", "verify", "blocked", "suspended"
- Limited to top 10 most relevant keywords per session

### Extraction Ethics

- **Passive only**: No active queries to solicit information
- **No entrapment**: Agent does not request UPI IDs, phone numbers, or bank details
- **No fabrication**: Intelligence is extracted exactly as provided by the sender

---

## 7. Cybercrime Reporting Readiness

### Structured Report Format

When a session completes, the system prepares a structured intelligence report suitable for cybercrime analysis:

- **Session metadata**: Unique identifier, message count, engagement duration
- **Scam classification**: Detected intent types (e.g., fake prize, UPI scam)
- **Extracted intelligence**: UPI IDs, phone numbers, URLs, bank accounts, keywords
- **Agent notes**: Summary of engagement and intelligence extraction

### Reporting Workflow

**This system does NOT directly file police complaints or cybercrime reports.**

Instead, it:
1. Generates structured data ready for integration with cybercrime platforms
2. Sends reports to a designated callback endpoint (hackathon evaluation endpoint in this implementation)
3. Provides data in a standardized format for analysis and investigation

### Intended Use

The structured reports enable:
- Pattern analysis across multiple scam sessions
- Identification of repeat scammers (matching UPI IDs, phone numbers)
- Domain/URL blacklisting based on phishing link intelligence
- Evidence collection for law enforcement investigations

Integration with official cybercrime portals (e.g., cybercrime.gov.in) would require additional authentication, compliance workflows, and legal review—outside the scope of this hackathon prototype.

---

## 8. Ethical & Security Considerations

### No Impersonation of Real Individuals

The agent does not:
- Claim to be a specific person, bank employee, or government official
- Use real names, addresses, or personally identifiable information
- Impersonate any organization or brand

Replies are generic and non-specific (e.g., "That sounds interesting, tell me more" rather than "I am [Name] from [Bank]").

### No Harassment or Illegal Instructions

The agent:
- Does not insult, threaten, or harass the message sender
- Does not provide instructions for illegal activities
- Terminates engagement after a maximum message count to avoid prolonged interaction

### Responsible Data Handling

- **No database persistence**: All session data is stored in memory only and discarded when the process stops
- **No logging of sensitive data**: Intelligence is logged internally for the session but not written to persistent files
- **No sharing beyond callback**: Extracted intelligence is sent only to the designated callback endpoint

### API Key-Based Security

- All API endpoints require authentication via `X-API-Key` header
- Prevents unauthorized access and abuse
- Configurable key via environment variables

### Session Limits

- Maximum messages per session (default: 20) prevents resource exhaustion
- Session timeout (default: 1 hour) automatically cleans up inactive sessions
- Prevents denial-of-service via excessive session creation

---

## 9. Evaluation Readiness

### Scam Detection Accuracy

**Measurement**: Proportion of scam messages correctly identified

- Rule-based patterns cover 7 major scam types
- Multi-label detection allows classification of hybrid scams
- Confidence scoring provides detection certainty (0.0 to 1.0)

**Limitations**: Rule-based approach may miss novel scam language not matching existing patterns. Future enhancement: ML-based intent classification.

### Engagement Depth

**Measurement**: Average message count and conversation duration per session

- Agent generates contextually appropriate replies to sustain engagement
- Progressive engagement: curiosity → interest → specific questions
- Natural variation prevents scammer suspicion

**Expected outcome**: 5-15 message exchanges for typical scam scenarios before session termination.

### Intelligence Quality

**Measurement**: Accuracy and completeness of extracted data

- Regex patterns tuned for Indian formats (UPI IDs, mobile numbers)
- Deduplication ensures no repeated entries
- Extraction is passive, so quality depends on scammer voluntarily providing information

**Expected outcome**: 70-90% of UPI IDs, phone numbers, and URLs provided by scammers will be correctly extracted.

### API Stability and Latency

**Measurement**: Response time and error rate under evaluation load

- FastAPI framework provides high-performance async handling
- In-memory session storage minimizes latency
- No external dependencies for core detection and reply generation

**Expected performance**:
- Response latency: < 200ms for typical requests
- Concurrent session support: 100+ active sessions
- Uptime: No crashes or unhandled exceptions during evaluation

### Mandatory Callback Compliance

**Requirement**: Final callback must be sent when scam is detected and engagement completes

- Callback URL hardcoded to hackathon endpoint: `https://hackathon.guvi.in/api/updateHoneyPotFinalResult`
- Callback triggered automatically on session termination (no manual intervention)
- Conditions enforced: scam detected AND minimum message threshold met
- Payload format matches hackathon specification exactly

**Testing**: Callback functionality validated via automated integration tests.

---

## 10. One-Line Summary

An autonomous backend API system that detects scam intent in messages, engages scammers through human-like multi-turn conversations without revealing detection, extracts structured intelligence (UPI IDs, phone numbers, phishing links), and provides ready-to-analyze reports for cybercrime investigation.

---

## Technical Implementation Summary

**Language**: Python 3.10+  
**Framework**: FastAPI  
**Dependencies**: httpx, pydantic, uvicorn  
**Architecture**: Stateless REST API with in-memory session management  
**Authentication**: API key-based (X-API-Key header)  
**Deployment**: Standalone backend service (no frontend)

**Key Endpoints**:
- `POST /api/honeypot` – Primary hackathon evaluation endpoint
- `GET /api/v1/health` – Health check
- `POST /api/v1/cleanup` – Session cleanup (authenticated)

**Configuration**:
- Environment variables via `.env` file
- Configurable session limits, timeouts, and thresholds
- Hardcoded callback URL for hackathon compliance

**Testing**:
- 51 automated tests covering API, integration, and unit levels
- All tests passing
- No security vulnerabilities detected (CodeQL scan)

---

## Acknowledgments

This solution addresses the need for actionable scam intelligence to support cybercrime investigation and prevention in India. The agentic honeypot approach enables passive intelligence gathering while maintaining ethical boundaries and security best practices.
