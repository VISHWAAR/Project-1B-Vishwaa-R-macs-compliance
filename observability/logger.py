"""
Structured Logger — 8-Category Logging Taxonomy

Provides structured logging for all agent activities, conforming to the
audit requirements specified in the compliance monitoring specification.

Log Categories:
  1. Agent Lifecycle       — startup, shutdown, health checks, config changes
  2. Detection Events      — pattern detection, threshold breach, anomaly ID
  3. Communication Events  — message sent, received, acknowledged, timeout
  4. Escalation Events     — escalation triggered, assigned, resolved, overridden
  5. Human Decision Events — review initiated, decision made, rationale documented
  6. Report Generation     — report triggered, validated, distributed, filed
  7. System Performance    — throughput, latency, queue depths, resource utilisation
  8. Security Events       — authentication, authorization, access denied, data access

Retention:
  - Regulatory events: 7 years (10 for SAR-related)
  - Operational events: 5 years
  - Diagnostic events: 1 year (rolling)
"""

import json
import logging
import time
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field, asdict

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Log Categories and Severity Levels
# ---------------------------------------------------------------------------

class LogCategory(str, Enum):
    AGENT_LIFECYCLE = "agent_lifecycle"
    DETECTION_EVENT = "detection_event"
    COMMUNICATION_EVENT = "communication_event"
    ESCALATION_EVENT = "escalation_event"
    HUMAN_DECISION = "human_decision"
    REPORT_GENERATION = "report_generation"
    SYSTEM_PERFORMANCE = "system_performance"
    SECURITY_EVENT = "security_event"


class Severity(str, Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARN = "WARN"
    ALERT = "ALERT"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"
    FATAL = "FATAL"


# Retention mapping (years)
RETENTION_YEARS: Dict[LogCategory, int] = {
    LogCategory.AGENT_LIFECYCLE: 7,
    LogCategory.DETECTION_EVENT: 7,
    LogCategory.COMMUNICATION_EVENT: 5,
    LogCategory.ESCALATION_EVENT: 7,
    LogCategory.HUMAN_DECISION: 10,
    LogCategory.REPORT_GENERATION: 7,
    LogCategory.SYSTEM_PERFORMANCE: 1,
    LogCategory.SECURITY_EVENT: 7,
}


# ---------------------------------------------------------------------------
# Structured Log Entry
# ---------------------------------------------------------------------------

@dataclass
class StructuredLogEntry:
    """A single structured log entry with full context."""
    entry_id: str = ""
    timestamp: str = ""
    category: str = ""
    severity: str = ""
    agent_id: str = ""
    event_type: str = ""
    message: str = ""
    trace_id: str = ""
    correlation_id: str = ""
    payload: Dict[str, Any] = field(default_factory=dict)
    duration_ms: Optional[float] = None
    previous_hash: str = ""
    entry_hash: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), default=str)


# ---------------------------------------------------------------------------
# Structured Logger
# ---------------------------------------------------------------------------

class StructuredLogger:
    """
    Audit-grade structured logger with 8-category taxonomy.

    Each log entry is serialized as JSON and can optionally be
    hashed for tamper-evidence via the AuditTrail.
    """

    def __init__(self):
        self._entries: List[StructuredLogEntry] = []
        self._counters: Dict[str, int] = {}

    def _next_id(self, category: LogCategory) -> str:
        key = category.value
        self._counters[key] = self._counters.get(key, 0) + 1
        return f"{key}-{self._counters[key]:06d}"

    def log(
        self,
        category: LogCategory,
        severity: Severity,
        agent_id: str,
        event_type: str,
        message: str,
        trace_id: str = "",
        correlation_id: str = "",
        payload: Optional[Dict[str, Any]] = None,
        duration_ms: Optional[float] = None,
    ) -> StructuredLogEntry:
        """Create and store a structured log entry."""
        entry = StructuredLogEntry(
            entry_id=self._next_id(category),
            timestamp=datetime.now(timezone.utc).isoformat(),
            category=category.value,
            severity=severity.value,
            agent_id=agent_id,
            event_type=event_type,
            message=message,
            trace_id=trace_id,
            correlation_id=correlation_id,
            payload=payload or {},
            duration_ms=duration_ms,
        )
        self._entries.append(entry)

        # Also log to Python's logging for console output
        log_fn = getattr(logger, severity.value.lower(), logger.info)
        log_fn(f"[{category.value}] [{agent_id}] {event_type}: {message}")

        return entry

    # -- Convenience methods for each category --

    def agent_started(self, agent_id: str, config: Optional[Dict] = None):
        return self.log(
            LogCategory.AGENT_LIFECYCLE, Severity.INFO, agent_id,
            "agent.started", f"Agent {agent_id} started",
            payload=config or {},
        )

    def agent_stopped(self, agent_id: str, reason: str = "normal"):
        return self.log(
            LogCategory.AGENT_LIFECYCLE, Severity.INFO, agent_id,
            "agent.stopped", f"Agent {agent_id} stopped: {reason}",
        )

    def agent_health_check(self, agent_id: str, status: str, metrics: Optional[Dict] = None):
        return self.log(
            LogCategory.AGENT_LIFECYCLE, Severity.INFO, agent_id,
            "agent.health_check", f"Health check: {status}",
            payload=metrics or {},
        )

    def detection(
        self,
        agent_id: str,
        violation_type: str,
        severity: Severity,
        description: str,
        confidence: float,
        trace_id: str = "",
        evidence: Optional[List[Dict]] = None,
    ):
        return self.log(
            LogCategory.DETECTION_EVENT, severity, agent_id,
            f"detection.{violation_type}",
            description,
            trace_id=trace_id,
            payload={
                "violation_type": violation_type,
                "confidence": confidence,
                "evidence_count": len(evidence) if evidence else 0,
            },
        )

    def message_sent(self, sender_id: str, recipient_id: str, msg_type: str, trace_id: str = ""):
        return self.log(
            LogCategory.COMMUNICATION_EVENT, Severity.INFO, sender_id,
            "message.sent", f"Sent {msg_type} to {recipient_id}",
            trace_id=trace_id,
            payload={"recipient": recipient_id, "message_type": msg_type},
        )

    def message_received(self, recipient_id: str, sender_id: str, msg_type: str, trace_id: str = ""):
        return self.log(
            LogCategory.COMMUNICATION_EVENT, Severity.INFO, recipient_id,
            "message.received", f"Received {msg_type} from {sender_id}",
            trace_id=trace_id,
            payload={"sender": sender_id, "message_type": msg_type},
        )

    def message_timeout(self, agent_id: str, message_id: str, elapsed_ms: float):
        return self.log(
            LogCategory.COMMUNICATION_EVENT, Severity.WARN, agent_id,
            "message.timeout", f"Message {message_id[:8]} timed out after {elapsed_ms:.0f}ms",
            payload={"message_id": message_id, "elapsed_ms": elapsed_ms},
        )

    def escalation_triggered(
        self, agent_id: str, escalation_id: str, from_tier: int, to_tier: int, reason: str, trace_id: str = ""
    ):
        return self.log(
            LogCategory.ESCALATION_EVENT, Severity.ALERT, agent_id,
            "escalation.triggered",
            f"Escalation {escalation_id[:8]}: Tier {from_tier} → {to_tier}: {reason}",
            trace_id=trace_id,
            payload={"escalation_id": escalation_id, "from_tier": from_tier, "to_tier": to_tier, "reason": reason},
        )

    def human_decision(
        self, agent_id: str, decision_id: str, decision: str, rationale: str, trace_id: str = ""
    ):
        return self.log(
            LogCategory.HUMAN_DECISION, Severity.ALERT, agent_id,
            "human.decision",
            f"Decision {decision_id[:8]}: {decision} — {rationale}",
            trace_id=trace_id,
            payload={"decision_id": decision_id, "decision": decision, "rationale": rationale},
        )

    def report_generated(
        self, agent_id: str, report_id: str, report_type: str, audience: str, trace_id: str = ""
    ):
        return self.log(
            LogCategory.REPORT_GENERATION, Severity.INFO, agent_id,
            "report.generated",
            f"Report {report_id[:8]} generated: {report_type} for {audience}",
            trace_id=trace_id,
            payload={"report_id": report_id, "report_type": report_type, "audience": audience},
        )

    def performance_metric(self, agent_id: str, metric_name: str, value: Any, trace_id: str = ""):
        return self.log(
            LogCategory.SYSTEM_PERFORMANCE, Severity.INFO, agent_id,
            f"performance.{metric_name}",
            f"{metric_name} = {value}",
            trace_id=trace_id,
            payload={"metric_name": metric_name, "value": value},
        )

    def security_event(self, agent_id: str, event_type: str, details: str, trace_id: str = ""):
        return self.log(
            LogCategory.SECURITY_EVENT, Severity.WARN, agent_id,
            f"security.{event_type}",
            details,
            trace_id=trace_id,
        )

    # -- Query --

    def get_entries(
        self,
        category: Optional[LogCategory] = None,
        agent_id: Optional[str] = None,
        severity: Optional[Severity] = None,
        trace_id: Optional[str] = None,
        limit: int = 100,
    ) -> List[StructuredLogEntry]:
        """Query log entries with optional filters."""
        results = self._entries
        if category:
            results = [e for e in results if e.category == category.value]
        if agent_id:
            results = [e for e in results if e.agent_id == agent_id]
        if severity:
            results = [e for e in results if e.severity == severity.value]
        if trace_id:
            results = [e for e in results if e.trace_id == trace_id]
        return results[-limit:]

    def get_audit_trail(self, trace_id: str) -> List[StructuredLogEntry]:
        """Get the complete audit trail for a specific trace."""
        return [e for e in self._entries if e.trace_id == trace_id]

    def get_summary(self) -> Dict[str, Any]:
        """Get a summary of logging activity."""
        by_category = {}
        for entry in self._entries:
            cat = entry.category
            by_category[cat] = by_category.get(cat, 0) + 1

        by_severity = {}
        for entry in self._entries:
            sev = entry.severity
            by_severity[sev] = by_severity.get(sev, 0) + 1

        return {
            "total_entries": len(self._entries),
            "by_category": by_category,
            "by_severity": by_severity,
            "retention_policy": {k.value: f"{v} years" for k, v in RETENTION_YEARS.items()},
        }


# ---------------------------------------------------------------------------
# Singleton
# ---------------------------------------------------------------------------

_structured_logger: Optional[StructuredLogger] = None


def get_structured_logger() -> StructuredLogger:
    """Get or create the global structured logger."""
    global _structured_logger
    if _structured_logger is None:
        _structured_logger = StructuredLogger()
    return _structured_logger
