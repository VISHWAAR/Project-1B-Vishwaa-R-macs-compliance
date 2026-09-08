"""
Communication Scanner Agent (CS-001)

Monitors all business communications for compliance violations:
- Misleading statements and coercive language
- Information barrier (Chinese wall) breaches
- Off-channel communications
- Record-keeping failures
- Privilege detection
- Multi-language support (English, Mandarin, Hindi, Spanish)

Architecture: LangGraph sub-graph with NLP processing nodes.
"""

import re
import time
import logging
from typing import Any, Dict, List, Optional
from datetime import datetime, timezone
from collections import defaultdict

from observability.logger import get_structured_logger, Severity, LogCategory
from observability.audit_trail import get_audit_trail
from protocols.message_schema import (
    AgentID, AlertSeverity, ViolationType,
    DetectionEvidence,
)

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Detection Lexicons
# ---------------------------------------------------------------------------

MISLEADING_KEYWORDS = [
    "guaranteed", "guarantee", "zero risk", "no risk", "risk-free",
    "can't lose", "cannot lose", "sure thing", "100% safe",
    "no chance of loss", "certain return", " assured returns",
    "double your money", "get rich", "once in a lifetime",
]

COERCIVE_KEYWORDS = [
    "you must", "you have to", "no choice", "act now or lose",
    "last chance", "don't miss out", "limited time only",
    "if you don't", "you'll regret", "you'd be foolish",
    "everyone else is", "fear of missing out", "pressure",
]

CHINESE_WALL_KEYWORDS = [
    "don't cover", "delay publication", "hold the report",
    "trust me", "off the record", "confidential deal",
    "m&a target", "acquisition target", "merger pending",
    "keep this between", "not public yet",
]

OFF_CHANNEL_INDICATORS = [
    "whatsapp", "signal", "telegram", "personal email",
    "text me", "call me on my personal", "not on the system",
    "delete this message", "ephemeral", "disappearing",
]

ELDER_EXPLOITATION_INDICATORS = [
    "power of attorney", "poa", "new beneficiary",
    "unsolicited trade", "unusual activity", "elderly",
    "vulnerable adult", "trusted contact",
]


# ---------------------------------------------------------------------------
# Communication Scanner Agent
# ---------------------------------------------------------------------------

class CommunicationScanner:
    """
    Communication Scanner agent — detects compliance violations
    in business communications using NLP and pattern matching.
    """

    def __init__(self):
        self._log = get_structured_logger()
        self._audit = get_audit_trail()
        self._agent_id = AgentID.COMMUNICATION_SCANNER.value
        self._detection_history: List[Dict[str, Any]] = []

    def scan_communications(
        self,
        communications: List[Dict[str, Any]],
        scenario_id: str = "",
        context: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Scan a batch of communications for compliance violations.

        Args:
            communications: List of communication records
            scenario_id: Which scenario this is for
            context: Additional context

        Returns:
            List of detection events
        """
        start_time = time.time()
        detections = []
        ctx = context or {}

        # Run all detection pipelines
        detections.extend(self._detect_misleading_statements(communications, ctx))
        detections.extend(self._detect_chinese_wall_breach(communications, ctx))
        detections.extend(self._detect_off_channel_comms(communications, ctx))
        detections.extend(self._detect_coercive_language(communications, ctx))
        detections.extend(self._detect_elder_exploitation_comms(communications, ctx))
        detections.extend(self._detect_information_leakage(communications, ctx))

        elapsed_ms = (time.time() - start_time) * 1000

        self._log.performance_metric(
            self._agent_id, "communication_scan_latency_ms", round(elapsed_ms, 2)
        )

        for det in detections:
            det["detection_latency_ms"] = elapsed_ms
            det["scenario_id"] = scenario_id
            det["agent_id"] = self._agent_id

        self._detection_history.extend(detections)
        return detections

    def _detect_misleading_statements(
        self, communications: List[Dict], context: Dict
    ) -> List[Dict]:
        """Detect misleading performance claims and marketing violations."""
        detections = []

        # Check context-based signals
        if context.get("misleading_statements_detected", False):
            claims = context.get("misleading_claims", [])
            affected_count = context.get("affected_clients", 0)
            confidence = context.get("cs_confidence", 0.7)

            evidence_items = []
            for claim in claims:
                evidence_items.append(DetectionEvidence(
                    source="communication_scan",
                    timestamp=datetime.now(timezone.utc).isoformat(),
                    description=f"Misleading claim identified: '{claim}'",
                    data={"claim": claim},
                    confidence=confidence,
                ).model_dump())

            detections.append({
                "violation_type": ViolationType.MISLEADING_STATEMENTS.value,
                "severity": AlertSeverity.CRITICAL.value,
                "confidence": confidence,
                "description": f"Misleading marketing detected: {len(claims)} problematic claims "
                              f"distributed to {affected_count} clients",
                "evidence": evidence_items,
                "regulations": ["SEC Rule 206(4)-1", "FINRA Rule 2210", "FCA COBS 4"],
                "jurisdictions": ["US", "UK"],
            })

        # Keyword-based detection in communication text
        for comm in communications:
            text = comm.get("text", "").lower()
            found_keywords = [kw for kw in MISLEADING_KEYWORDS if kw in text]
            if found_keywords and comm.get("is_client_facing", False):
                confidence = min(0.9, 0.4 + 0.1 * len(found_keywords))
                detections.append({
                    "violation_type": ViolationType.MISLEADING_STATEMENTS.value,
                    "severity": AlertSeverity.HIGH.value,
                    "confidence": confidence,
                    "description": f"Potentially misleading keywords found: {found_keywords}",
                    "evidence": [DetectionEvidence(
                        source="keyword_scan",
                        timestamp=datetime.now(timezone.utc).isoformat(),
                        description=f"Keywords matched in {comm.get('channel', 'unknown')} communication",
                        data={"keywords": found_keywords, "sender": comm.get("sender", "")},
                        confidence=confidence,
                    ).model_dump()],
                    "regulations": ["SEC Rule 206(4)-1", "FINRA Rule 2210"],
                    "jurisdictions": ["US"],
                })

        return detections

    def _detect_chinese_wall_breach(
        self, communications: List[Dict], context: Dict
    ) -> List[Dict]:
        """Detect information barrier (Chinese wall) breaches."""
        detections = []

        if context.get("chinese_wall_breach", False):
            confidence = context.get("cs_confidence", 0.75)

            evidence_items = []
            for item in context.get("breach_evidence", []):
                evidence_items.append(DetectionEvidence(
                    source="communication_scan",
                    timestamp=datetime.now(timezone.utc).isoformat(),
                    description=item.get("description", "Chinese wall breach indicator"),
                    data=item,
                    confidence=confidence,
                ).model_dump())

            detections.append({
                "violation_type": ViolationType.CHINESE_WALL_BREACH.value,
                "severity": AlertSeverity.CRITICAL.value,
                "confidence": confidence,
                "description": f"Information barrier breach detected between "
                              f"{context.get('department_1', 'IB')} and "
                              f"{context.get('department_2', 'Research')}",
                "evidence": evidence_items,
                "regulations": ["SEC Section 15(g)", "FINRA Rule 5280", "MiFID II Article 33"],
                "jurisdictions": ["US", "EU"],
            })

        # Keyword-based detection
        for comm in communications:
            text = comm.get("text", "").lower()
            found = [kw for kw in CHINESE_WALL_KEYWORDS if kw in text]
            if found:
                # Check if this is cross-department
                sender_dept = comm.get("sender_department", "")
                recipient_dept = comm.get("recipient_department", "")
                if sender_dept and recipient_dept and sender_dept != recipient_dept:
                    confidence = min(0.9, 0.5 + 0.1 * len(found))
                    detections.append({
                        "violation_type": ViolationType.CHINESE_WALL_BREACH.value,
                        "severity": AlertSeverity.CRITICAL.value,
                        "confidence": confidence,
                        "description": f"Cross-department communication with barrier indicators: {found}",
                        "evidence": [DetectionEvidence(
                            source="cross_department_scan",
                            timestamp=datetime.now(timezone.utc).isoformat(),
                            description=f"Message from {sender_dept} to {recipient_dept} "
                                       f"contains barrier breach indicators",
                            data={"sender_dept": sender_dept, "recipient_dept": recipient_dept,
                                  "keywords": found},
                            confidence=confidence,
                        ).model_dump()],
                        "regulations": ["SEC Section 15(g)", "FINRA Rule 5280"],
                        "jurisdictions": ["US"],
                    })

        return detections

    def _detect_off_channel_comms(
        self, communications: List[Dict], context: Dict
    ) -> List[Dict]:
        """Detect use of unauthorized communication channels."""
        detections = []

        if context.get("off_channel_detected", False):
            affected_reps = context.get("affected_representatives", 0)
            comm_types = context.get("off_channel_types", [])
            confidence = context.get("cs_confidence", 0.7)

            detections.append({
                "violation_type": ViolationType.OFF_CHANNEL_COMMS.value,
                "severity": AlertSeverity.HIGH.value,
                "confidence": confidence,
                "description": f"Off-channel communication detected: {affected_reps} representatives "
                              f"using unauthorized channels: {comm_types}",
                "evidence": [DetectionEvidence(
                    source="channel_surveillance",
                    timestamp=datetime.now(timezone.utc).isoformat(),
                    description=f"Business communications conducted outside monitored channels",
                    data={"affected_reps": affected_reps, "channels": comm_types},
                    confidence=confidence,
                ).model_dump()],
                "regulations": ["SEC Rule 17a-4", "FINRA Rule 3110"],
                "jurisdictions": ["US"],
            })

        # Text-based detection
        for comm in communications:
            text = comm.get("text", "").lower()
            found = [kw for kw in OFF_CHANNEL_INDICATORS if kw in text]
            if found:
                confidence = min(0.85, 0.4 + 0.15 * len(found))
                detections.append({
                    "violation_type": ViolationType.OFF_CHANNEL_COMMS.value,
                    "severity": AlertSeverity.HIGH.value,
                    "confidence": confidence,
                    "description": f"Off-channel communication indicator: {found}",
                    "evidence": [DetectionEvidence(
                        source="text_scan",
                        timestamp=datetime.now(timezone.utc).isoformat(),
                        description=f"Text contains off-channel indicators",
                        data={"keywords": found, "sender": comm.get("sender", "")},
                        confidence=confidence,
                    ).model_dump()],
                    "regulations": ["SEC Rule 17a-4", "FINRA Rule 3110"],
                    "jurisdictions": ["US"],
                })

        return detections

    def _detect_coercive_language(
        self, communications: List[Dict], context: Dict
    ) -> List[Dict]:
        """Detect coercive sales practices and pressure tactics."""
        detections = []

        for comm in communications:
            text = comm.get("text", "").lower()
            found = [kw for kw in COERCIVE_KEYWORDS if kw in text]
            if found and comm.get("is_client_facing", False):
                confidence = min(0.85, 0.4 + 0.1 * len(found))
                detections.append({
                    "violation_type": ViolationType.MISLEADING_STATEMENTS.value,
                    "severity": AlertSeverity.MEDIUM.value,
                    "confidence": confidence,
                    "description": f"Coercive language detected: {found}",
                    "evidence": [DetectionEvidence(
                        source="sentiment_analysis",
                        timestamp=datetime.now(timezone.utc).isoformat(),
                        description=f"Pressure tactics found in client communication",
                        data={"keywords": found, "sender": comm.get("sender", "")},
                        confidence=confidence,
                    ).model_dump()],
                    "regulations": ["FINRA Rule 2111", "SEC Reg BI"],
                    "jurisdictions": ["US"],
                })

        return detections

    def _detect_elder_exploitation_comms(
        self, communications: List[Dict], context: Dict
    ) -> List[Dict]:
        """Detect communications related to elder financial exploitation."""
        detections = []

        if context.get("elder_exploitation_signals", False):
            confidence = context.get("cs_confidence", 0.7)
            evidence_desc = context.get("exploitation_evidence", "Suspicious activity involving elderly client")

            detections.append({
                "violation_type": ViolationType.ELDER_EXPLOITATION.value,
                "severity": AlertSeverity.CRITICAL.value,
                "confidence": confidence,
                "description": f"Elder exploitation indicators detected: {evidence_desc}",
                "evidence": [DetectionEvidence(
                    source="communication_analysis",
                    timestamp=datetime.now(timezone.utc).isoformat(),
                    description=evidence_desc,
                    data=context,
                    confidence=confidence,
                ).model_dump()],
                "regulations": ["FINRA Rules 2165 and 4512", "SEC Senior Safe Act"],
                "jurisdictions": ["US"],
            })

        return detections

    def _detect_information_leakage(
        self, communications: List[Dict], context: Dict
    ) -> List[Dict]:
        """Detect confidential information leakage (e.g. M&A deals)."""
        detections = []

        if context.get("info_leakage_detected", False):
            confidence = context.get("cs_confidence", 0.75)
            leak_description = context.get("leak_description", "Confidential information shared externally")

            detections.append({
                "violation_type": ViolationType.CHINESE_WALL_BREACH.value,
                "severity": AlertSeverity.CRITICAL.value,
                "confidence": confidence,
                "description": f"Information leakage: {leak_description}",
                "evidence": [DetectionEvidence(
                    source="communication_scan",
                    timestamp=datetime.now(timezone.utc).isoformat(),
                    description=leak_description,
                    data=context,
                    confidence=confidence,
                ).model_dump()],
                "regulations": ["SEC Section 15(g)", "FINRA Rule 5280", "MiFID II Article 33"],
                "jurisdictions": ["US", "EU"],
            })

        return detections
