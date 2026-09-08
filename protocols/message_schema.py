"""
Inter-Agent Message Schema — Pydantic Models

Defines the complete message format for all agent-to-agent communication.
Based on the specification in the PDF (Appendix B: Sample Inter-Agent Message Schema).

Every message flowing between agents MUST conform to these schemas.
"""

import uuid
from enum import Enum
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field, field_validator


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class MessageType(str, Enum):
    """Types of inter-agent messages."""
    ALERT = "ALERT"
    QUERY = "QUERY"
    RESPONSE = "RESPONSE"
    UPDATE = "UPDATE"
    HEARTBEAT = "HEARTBEAT"
    ESCALATION = "ESCALATION"


class Priority(int, Enum):
    """Message priority levels with associated SLAs."""
    CRITICAL = 1   # SLA: 15 minutes
    HIGH = 2       # SLA: 1 hour
    MEDIUM = 3     # SLA: 4 hours
    LOW = 4        # SLA: 24 hours
    INFORMATIONAL = 5  # SLA: best effort


class AuditClassification(str, Enum):
    """Determines log retention period."""
    REGULATORY = "REGULATORY"   # 7-10 years
    OPERATIONAL = "OPERATIONAL" # 5 years
    DIAGNOSTIC = "DIAGNOSTIC"   # 1 year


class ViolationType(str, Enum):
    """Classification of detected compliance violations."""
    INSIDER_TRADING = "INSIDER_TRADING"
    MARKET_MANIPULATION = "MARKET_MANIPULATION"
    SPOOFING_LAYERING = "SPOOFING_LAYERING"
    WASH_TRADING = "WASH_TRADING"
    FRONT_RUNNING = "FRONT_RUNNING"
    LATE_TRADING = "LATE_TRADING"
    AML_STRUCTURING = "AML_STRUCTURING"
    SANCTIONS_VIOLATION = "SANCTIONS_VIOLATION"
    SUITABILITY_VIOLATION = "SUITABILITY_VIOLATION"
    MISLEADING_STATEMENTS = "MISLEADING_STATEMENTS"
    CHINESE_WALL_BREACH = "CHINESE_WALL_BREACH"
    OFF_CHANNEL_COMMS = "OFF_CHANNEL_COMMS"
    RECORD_KEEPING_FAILURE = "RECORD_KEEPING_FAILURE"
    BEST_EXECUTION_FAILURE = "BEST_EXECUTION_FAILURE"
    CONCENTRATION_RISK = "CONCENTRATION_RISK"
    DATA_PRIVACY_VIOLATION = "DATA_PRIVACY_VIOLATION"
    RESEARCH_INDEPENDENCE = "RESEARCH_INDEPENDENCE"
    ELDER_EXPLOITATION = "ELDER_EXPLOITATION"
    REGULATORY_CHANGE = "REGULATORY_CHANGE"
    CONFLICT_OF_INTEREST = "CONFLICT_OF_INTEREST"
    COORDINATED_VIOLATION = "COORDINATED_VIOLATION"


class AlertSeverity(str, Enum):
    """Alert severity levels for detected violations."""
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    NO_ALERT = "NO_ALERT"


class AgentID(str, Enum):
    """Unique identifiers for all agents in the system."""
    ORCHESTRATOR = "ORCH-001"
    TRANSACTION_MONITOR = "TM-001"
    COMMUNICATION_SCANNER = "CS-001"
    REGULATORY_TRACKER = "RU-001"
    REPORT_GENERATOR = "RG-001"


# ---------------------------------------------------------------------------
# Message Envelope — the core message structure
# ---------------------------------------------------------------------------

class MessageEnvelope(BaseModel):
    """
    Core message envelope for all inter-agent communication.
    Every message between agents MUST be wrapped in this envelope.

    Based on Appendix B of the specification document.
    """
    # Identity
    message_id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        description="Globally unique message identifier (UUID v4)"
    )
    protocol_version: str = Field(
        default="1.0.0",
        description="Semantic versioning for the protocol"
    )
    timestamp: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(),
        description="ISO 8601 UTC timestamp with millisecond precision"
    )

    # Routing
    sender_agent_id: str = Field(
        description="Unique identifier of the sending agent"
    )
    recipient_agent_id: Union[str, List[str]] = Field(
        description="Target agent(s) — single ID or array for multicast"
    )
    message_type: MessageType = Field(
        description="ALERT, QUERY, RESPONSE, UPDATE, HEARTBEAT, ESCALATION"
    )
    priority: Priority = Field(
        default=Priority.MEDIUM,
        description="1=CRITICAL, 2=HIGH, 3=MEDIUM, 4=LOW, 5=INFORMATIONAL"
    )

    # Tracing
    correlation_id: Optional[str] = Field(
        default=None,
        description="Links related messages in a conversation chain"
    )
    trace_id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        description="Distributed tracing identifier for observability"
    )

    # Payload
    payload_schema: str = Field(
        description="Schema identifier (e.g. alert.insider-trading.v2)"
    )
    payload: Dict[str, Any] = Field(
        default_factory=dict,
        description="Message-type-specific structured content"
    )

    # Confidence
    confidence_score: Optional[float] = Field(
        default=None,
        ge=0.0, le=1.0,
        description="Agent's confidence in the assessment (0.0-1.0)"
    )

    # Delivery
    ttl_seconds: int = Field(
        default=3600,
        description="Time-to-live — message expires after this duration"
    )
    retry_count: int = Field(
        default=0,
        description="Number of delivery attempts (0 for first)"
    )

    # Audit
    audit_classification: AuditClassification = Field(
        default=AuditClassification.OPERATIONAL,
        description="REGULATORY, OPERATIONAL, DIAGNOSTIC — determines retention"
    )

    # Security
    sender_signature: str = Field(
        default="",
        description="Cryptographic signature for message authentication"
    )
    nonce: str = Field(
        default_factory=lambda: uuid.uuid4().hex[:16],
        description="One-time value for replay prevention"
    )

    def is_expired(self) -> bool:
        """Check if the message has exceeded its TTL."""
        msg_time = datetime.fromisoformat(self.timestamp)
        now = datetime.now(timezone.utc)
        return (now - msg_time).total_seconds() > self.ttl_seconds


# ---------------------------------------------------------------------------
# Detection Event Payloads
# ---------------------------------------------------------------------------

class DetectionEvidence(BaseModel):
    """Individual piece of evidence supporting a detection."""
    evidence_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    source: str = Field(description="Source of the evidence (e.g. 'transaction_log', 'email_scan')")
    timestamp: str = Field(description="When the evidence was observed")
    description: str = Field(description="Human-readable description")
    data: Dict[str, Any] = Field(default_factory=dict, description="Raw evidence data")
    confidence: float = Field(ge=0.0, le=1.0, description="Confidence in this evidence")


class DetectionPayload(BaseModel):
    """Payload for ALERT messages containing detection events."""
    scenario_id: str = Field(description="Compliance scenario ID (e.g. CS-01)")
    violation_type: ViolationType = Field(description="Type of violation detected")
    severity: AlertSeverity = Field(description="Alert severity level")
    description: str = Field(description="Human-readable description of the detection")
    evidence: List[DetectionEvidence] = Field(default_factory=list, description="Supporting evidence")
    affected_jurisdictions: List[str] = Field(default_factory=list, description="Affected regulatory jurisdictions")
    applicable_regulations: List[str] = Field(default_factory=list, description="Specific regulations violated")
    confidence_score: float = Field(ge=0.0, le=1.0, description="Overall detection confidence")
    detection_latency_ms: float = Field(default=0.0, description="Time from event to detection in ms")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional context")


# ---------------------------------------------------------------------------
# Escalation Payload
# ---------------------------------------------------------------------------

class EscalationPayload(BaseModel):
    """Payload for ESCALATION messages."""
    escalation_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    detection_id: str = Field(description="Reference to the original detection message")
    current_tier: int = Field(ge=1, le=4, description="Current escalation tier (1-4)")
    target_tier: int = Field(ge=1, le=4, description="Target escalation tier")
    reason: str = Field(description="Reason for escalation")
    sla_deadline: str = Field(description="ISO 8601 deadline for response")
    agent_assessments: Dict[str, Dict[str, Any]] = Field(
        default_factory=dict,
        description="Assessments from each agent involved"
    )
    conflict_summary: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Summary of any inter-agent conflicts"
    )
    recommended_actions: List[str] = Field(
        default_factory=list,
        description="System-recommended actions for the human reviewer"
    )
    regulatory_citations: List[str] = Field(
        default_factory=list,
        description="Specific regulatory provisions relevant to this escalation"
    )
    similar_cases: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Historical similar cases for reference"
    )


# ---------------------------------------------------------------------------
# Query / Response Payloads
# ---------------------------------------------------------------------------

class QueryPayload(BaseModel):
    """Payload for QUERY messages — one agent requesting data from another."""
    query_type: str = Field(description="Type of query (e.g. 'transaction_lookup', 'regulation_check')")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Query parameters")
    context: str = Field(default="", description="Why this query is being made")
    response_required: bool = Field(default=True, description="Whether a RESPONSE is expected")
    timeout_seconds: int = Field(default=30, description="Max time to wait for response")


class ResponsePayload(BaseModel):
    """Payload for RESPONSE messages — answering a QUERY."""
    query_id: str = Field(description="message_id of the original QUERY")
    success: bool = Field(description="Whether the query was answered successfully")
    data: Dict[str, Any] = Field(default_factory=dict, description="Response data")
    error: Optional[str] = Field(default=None, description="Error message if query failed")
    confidence: float = Field(ge=0.0, le=1.0, description="Confidence in the response data")


# ---------------------------------------------------------------------------
# Update Payload
# ---------------------------------------------------------------------------

class UpdatePayload(BaseModel):
    """Payload for UPDATE messages — broadcasting state changes."""
    update_type: str = Field(description="Type of update (e.g. 'regulatory_change', 'threshold_update')")
    source_agent: str = Field(description="Agent that generated the update")
    content: Dict[str, Any] = Field(default_factory=dict, description="Update content")
    effective_date: Optional[str] = Field(default=None, description="When the update takes effect")
    affected_agents: List[str] = Field(default_factory=list, description="Agents affected by this update")


# ---------------------------------------------------------------------------
# Heartbeat Payload
# ---------------------------------------------------------------------------

class HeartbeatPayload(BaseModel):
    """Payload for HEARTBEAT messages — agent health monitoring."""
    status: str = Field(description="Agent status: running, degraded, stopped")
    uptime_seconds: float = Field(description="How long the agent has been running")
    queue_depth: int = Field(default=0, description="Number of pending items in agent queue")
    cpu_usage_percent: float = Field(default=0.0, description="Current CPU usage")
    memory_usage_mb: float = Field(default=0.0, description="Current memory usage in MB")
    last_detection: Optional[str] = Field(default=None, description="Timestamp of last detection")
    error_rate: float = Field(default=0.0, description="Error rate over last measurement window")
    custom_metrics: Dict[str, Any] = Field(default_factory=dict)


# ---------------------------------------------------------------------------
# Convenience constructors
# ---------------------------------------------------------------------------

def create_detection_message(
    sender: AgentID,
    scenario_id: str,
    violation_type: ViolationType,
    severity: AlertSeverity,
    description: str,
    confidence: float,
    evidence: Optional[List[DetectionEvidence]] = None,
    regulations: Optional[List[str]] = None,
    jurisdictions: Optional[List[str]] = None,
    recipients: Optional[List[AgentID]] = None,
) -> MessageEnvelope:
    """Create an ALERT message for a compliance detection."""
    payload = DetectionPayload(
        scenario_id=scenario_id,
        violation_type=violation_type,
        severity=severity,
        description=description,
        evidence=evidence or [],
        affected_jurisdictions=jurisdictions or [],
        applicable_regulations=regulations or [],
        confidence_score=confidence,
    )
    return MessageEnvelope(
        sender_agent_id=sender.value,
        recipient_agent_id=[r.value for r in recipients] if recipients else AgentID.ORCHESTRATOR.value,
        message_type=MessageType.ALERT,
        priority=Priority.CRITICAL if severity == AlertSeverity.CRITICAL else (
            Priority.HIGH if severity == AlertSeverity.HIGH else Priority.MEDIUM
        ),
        payload_schema=f"detection.{violation_type.value.lower()}.v1",
        payload=payload.model_dump(),
        confidence_score=confidence,
        audit_classification=AuditClassification.REGULATORY,
    )


def create_escalation_message(
    sender: AgentID,
    detection_id: str,
    current_tier: int,
    target_tier: int,
    reason: str,
    agent_assessments: Dict[str, Dict[str, Any]],
    recommended_actions: Optional[List[str]] = None,
    regulations: Optional[List[str]] = None,
) -> MessageEnvelope:
    """Create an ESCALATION message."""
    from datetime import timedelta
    sla_hours = {1: 0.25, 2: 1, 3: 4, 4: 24}
    deadline = datetime.now(timezone.utc) + timedelta(hours=sla_hours.get(target_tier, 4))

    payload = EscalationPayload(
        detection_id=detection_id,
        current_tier=current_tier,
        target_tier=target_tier,
        reason=reason,
        sla_deadline=deadline.isoformat(),
        agent_assessments=agent_assessments,
        recommended_actions=recommended_actions or [],
        regulatory_citations=regulations or [],
    )
    return MessageEnvelope(
        sender_agent_id=sender.value,
        recipient_agent_id=AgentID.ORCHESTRATOR.value,
        message_type=MessageType.ESCALATION,
        priority=Priority.CRITICAL if target_tier >= 3 else Priority.HIGH,
        payload_schema="escalation.standard.v1",
        payload=payload.model_dump(),
        confidence_score=None,
        audit_classification=AuditClassification.REGULATORY,
    )
