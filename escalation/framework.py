"""
Escalation Framework — Human-in-the-Loop System

4-Tier Structure:
  Tier 1: Analyst          — SLA: 15 minutes
  Tier 2: Senior Analyst   — SLA: 1 hour
  Tier 3: Manager          — SLA: 4 hours
  Tier 4: Director/CCO     — SLA: 24 hours

Features:
  - Configurable escalation triggers with thresholds
  - Decision support packages for human reviewers
  - Auto-re-escalation when SLAs are missed
  - Authorization controls for human overrides
  - Feedback loop to improve agent performance
"""

import os
import time
import logging
from datetime import datetime, timezone, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Escalation Configuration
# ---------------------------------------------------------------------------

class EscalationTier(int, Enum):
    TIER_1_ANALYST = 1
    TIER_2_SENIOR = 2
    TIER_3_MANAGER = 3
    TIER_4_DIRECTOR = 4


# SLA in seconds per tier
DEFAULT_SLAS = {
    EscalationTier.TIER_1_ANALYST: 900,       # 15 minutes
    EscalationTier.TIER_2_SENIOR: 3600,       # 1 hour
    EscalationTier.TIER_3_MANAGER: 14400,     # 4 hours
    EscalationTier.TIER_4_DIRECTOR: 86400,    # 24 hours
}

TIER_NAMES = {
    EscalationTier.TIER_1_ANALYST: "Analyst",
    EscalationTier.TIER_2_SENIOR: "Senior Analyst",
    EscalationTier.TIER_3_MANAGER: "Compliance Manager",
    EscalationTier.TIER_4_DIRECTOR: "Director/CCO",
}

TIER_AUTHORITIES = {
    EscalationTier.TIER_1_ANALYST: [
        "acknowledge_alert", "request_more_data", "dismiss_false_positive",
    ],
    EscalationTier.TIER_2_SENIOR: [
        "acknowledge_alert", "request_more_data", "dismiss_false_positive",
        "initiate_investigation", "modify_thresholds",
    ],
    EscalationTier.TIER_3_MANAGER: [
        "acknowledge_alert", "request_more_data", "dismiss_false_positive",
        "initiate_investigation", "modify_thresholds",
        "file_sar", "notify_regulator", "initiate_trade_halt",
    ],
    EscalationTier.TIER_4_DIRECTOR: [
        "acknowledge_alert", "request_more_data", "dismiss_false_positive",
        "initiate_investigation", "modify_thresholds",
        "file_sar", "notify_regulator", "initiate_trade_halt",
        "board_notification", "self_report_to_regulator",
    ],
}


# ---------------------------------------------------------------------------
# Escalation Triggers
# ---------------------------------------------------------------------------

class EscalationTrigger(Enum):
    """Types of triggers that cause escalation."""
    HIGH_CONFIDENCE_DETECTION = "high_confidence_detection"
    CRITICAL_SEVERITY = "critical_severity"
    MULTI_AGENT_CONFLICT = "multi_agent_conflict"
    SLA_BREACH = "sla_breach"
    RECURRING_VIOLATION = "recurring_violation"
    REGULATORY_DEADLINE = "regulatory_deadline"
    CROSS_JURISDICTIONAL = "cross_jurisdictional"
    HUMAN_OVERRIDE_REQUEST = "human_override_request"


# Trigger conditions (thresholds)
TRIGGER_THRESHOLDS = {
    EscalationTrigger.HIGH_CONFIDENCE_DETECTION: {"min_confidence": 0.8},
    EscalationTrigger.CRITICAL_SEVERITY: {"severity": "CRITICAL"},
    EscalationTrigger.MULTI_AGENT_CONFLICT: {"min_conflicting_agents": 2},
    EscalationTrigger.SLA_BREACH: {"min_overdue_seconds": 300},
    EscalationTrigger.RECURRING_VIOLATION: {"min_occurrences": 3},
    EscalationTrigger.CROSS_JURISDICTIONAL: {"min_jurisdictions": 2},
}


def evaluate_triggers(
    detection_data: Dict[str, Any],
    agent_assessments: Dict[str, Dict[str, Any]],
) -> List[EscalationTrigger]:
    """Evaluate which escalation triggers are activated for a detection."""
    triggered = []

    confidence = detection_data.get("confidence", 0)
    if confidence >= TRIGGER_THRESHOLDS[EscalationTrigger.HIGH_CONFIDENCE_DETECTION]["min_confidence"]:
        triggered.append(EscalationTrigger.HIGH_CONFIDENCE_DETECTION)

    severity = detection_data.get("severity", "MEDIUM")
    if severity == "CRITICAL":
        triggered.append(EscalationTrigger.CRITICAL_SEVERITY)

    # Count conflicting agents
    detecting = sum(1 for a in agent_assessments.values() if a.get("detected", False))
    not_detecting = sum(1 for a in agent_assessments.values() if not a.get("detected", False))
    if detecting > 0 and not_detecting > 0:
        triggered.append(EscalationTrigger.MULTI_AGENT_CONFLICT)

    jurisdictions = detection_data.get("jurisdictions", [])
    if len(jurisdictions) >= 2:
        triggered.append(EscalationTrigger.CROSS_JURISDICTIONAL)

    return triggered


# ---------------------------------------------------------------------------
# Decision Support Package
# ---------------------------------------------------------------------------

@dataclass
class DecisionSupportPackage:
    """Comprehensive information for human decision-making."""
    detection_summary: Dict[str, Any]
    agent_assessments: Dict[str, Dict[str, Any]]
    consensus_result: Dict[str, Any]
    evidence_summary: List[Dict[str, Any]]
    regulatory_citations: List[str]
    similar_cases: List[Dict[str, Any]]
    recommended_actions: List[str]
    risk_assessment: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "detection_summary": self.detection_summary,
            "agent_assessments": self.agent_assessments,
            "consensus_result": self.consensus_result,
            "evidence_summary": self.evidence_summary,
            "regulatory_citations": self.regulatory_citations,
            "similar_cases": self.similar_cases,
            "recommended_actions": self.recommended_actions,
            "risk_assessment": self.risk_assessment,
        }


def build_decision_support_package(
    detection_data: Dict[str, Any],
    agent_assessments: Dict[str, Dict[str, Any]],
    consensus_result: Dict[str, Any],
) -> DecisionSupportPackage:
    """Build a decision support package for human review."""
    evidence = []
    for agent_id, data in agent_assessments.items():
        if data.get("detected", False):
            evidence.append({
                "source_agent": agent_id,
                "confidence": data.get("confidence", 0),
                "severity": data.get("severity", "MEDIUM"),
                "description": data.get("description", ""),
                "evidence": data.get("evidence", []),
            })

    # Build recommended actions
    recommended = []
    severity = detection_data.get("severity", "MEDIUM")
    if severity in ("CRITICAL", "HIGH"):
        recommended.append("Initiate immediate investigation")
        recommended.append("Preserve all related communications and records")
    if severity == "CRITICAL":
        recommended.append("Notify senior management within 24 hours")
    if detection_data.get("requires_sar", False):
        recommended.append("Prepare Suspicious Activity Report (SAR)")

    return DecisionSupportPackage(
        detection_summary={
            "violation_type": detection_data.get("violation_type", "unknown"),
            "severity": severity,
            "confidence": detection_data.get("confidence", 0),
            "description": detection_data.get("description", ""),
            "scenario_id": detection_data.get("scenario_id", ""),
        },
        agent_assessments=agent_assessments,
        consensus_result=consensus_result,
        evidence_summary=evidence,
        regulatory_citations=detection_data.get("regulations", []),
        similar_cases=[],
        recommended_actions=recommended,
        risk_assessment={
            "financial_risk": "high" if severity == "CRITICAL" else "medium",
            "regulatory_risk": "high",
            "reputational_risk": "high" if severity in ("CRITICAL", "HIGH") else "medium",
        },
    )


# ---------------------------------------------------------------------------
# Escalation Manager
# ---------------------------------------------------------------------------

@dataclass
class EscalationRecord:
    """A record of an escalation event."""
    escalation_id: str
    detection_id: str
    current_tier: EscalationTier
    triggered_by: List[EscalationTrigger]
    decision_support: DecisionSupportPackage
    created_at: str = ""
    resolved_at: Optional[str] = None
    resolved_by: Optional[str] = None
    decision: Optional[str] = None
    rationale: Optional[str] = None
    auto_escalated: bool = False

    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now(timezone.utc).isoformat()


class EscalationFramework:
    """
    Manages the complete escalation lifecycle:
    trigger evaluation → tier assignment → SLA monitoring → auto-re-escalation → resolution
    """

    def __init__(self, slas: Optional[Dict[EscalationTier, int]] = None):
        self._slas = slas or DEFAULT_SLAS
        self._active_escalations: Dict[str, EscalationRecord] = {}
        self._resolved_escalations: List[EscalationRecord] = []
        self._escalation_counter = 0

    def create_escalation(
        self,
        detection_id: str,
        detection_data: Dict[str, Any],
        agent_assessments: Dict[str, Dict[str, Any]],
        consensus_result: Dict[str, Any],
    ) -> EscalationRecord:
        """Create a new escalation from a detection event."""
        triggers = evaluate_triggers(detection_data, agent_assessments)
        tier = self._determine_initial_tier(triggers, detection_data)

        self._escalation_counter += 1
        escalation_id = f"ESC-{self._escalation_counter:06d}"

        dsp = build_decision_support_package(detection_data, agent_assessments, consensus_result)

        record = EscalationRecord(
            escalation_id=escalation_id,
            detection_id=detection_id,
            current_tier=tier,
            triggered_by=triggers,
            decision_support=dsp,
        )

        self._active_escalations[escalation_id] = record
        logger.info(
            f"Escalation {escalation_id} created: Tier {tier.value} "
            f"({TIER_NAMES[tier]}), triggers: {[t.value for t in triggers]}"
        )
        return record

    def _determine_initial_tier(
        self,
        triggers: List[EscalationTrigger],
        detection_data: Dict[str, Any],
    ) -> EscalationTier:
        """Determine the initial escalation tier based on triggers."""
        severity = detection_data.get("severity", "MEDIUM")

        # CRITICAL severity → Tier 3 minimum
        if severity == "CRITICAL":
            if EscalationTrigger.CROSS_JURISDICTIONAL in triggers:
                return EscalationTier.TIER_4_DIRECTOR
            return EscalationTier.TIER_3_MANAGER

        # HIGH severity or multi-agent conflict → Tier 2
        if severity == "HIGH" or EscalationTrigger.MULTI_AGENT_CONFLICT in triggers:
            return EscalationTier.TIER_2_SENIOR

        # Default → Tier 1
        return EscalationTier.TIER_1_ANALYST

    def handle_decision(
        self,
        escalation_id: str,
        decision: str,
        rationale: str,
        decided_by: str,
    ) -> Optional[EscalationRecord]:
        """
        Record a human decision on an escalation.

        Args:
            escalation_id: The escalation to resolve
            decision: The decision made (e.g. 'approve', 'dismiss', 'escalate')
            rationale: Explanation of the decision
            decided_by: Who made the decision
        """
        record = self._active_escalations.get(escalation_id)
        if not record:
            logger.warning(f"Escalation {escalation_id} not found in active escalations")
            return None

        # Check authorization
        tier = record.current_tier
        if decision in ("file_sar", "notify_regulator", "initiate_trade_halt"):
            min_tier = EscalationTier.TIER_3_MANAGER
            if tier < min_tier:
                logger.warning(
                    f"Decision '{decision}' requires Tier {min_tier.value}+ "
                    f"but current tier is {tier.value}"
                )

        record.resolved_at = datetime.now(timezone.utc).isoformat()
        record.resolved_by = decided_by
        record.decision = decision
        record.rationale = rationale

        # Move to resolved
        self._active_escalations.pop(escalation_id, None)
        self._resolved_escalations.append(record)

        logger.info(f"Escalation {escalation_id} resolved: {decision} by {decided_by}")
        return record

    def check_auto_escalation(self) -> List[EscalationRecord]:
        """
        Check for SLA breaches and auto-escalate if needed.

        Returns list of escalations that were auto-escalated.
        """
        auto_escalated = []
        now = datetime.now(timezone.utc)

        for escalation_id, record in list(self._active_escalations.items()):
            created = datetime.fromisoformat(record.created_at)
            elapsed = (now - created).total_seconds()
            sla = self._slas.get(record.current_tier, 86400)

            if elapsed > sla:
                # SLA breached — escalate to next tier
                current = record.current_tier
                if current.value < EscalationTier.TIER_4_DIRECTOR.value:
                    new_tier = EscalationTier(current.value + 1)
                    record.current_tier = new_tier
                    record.auto_escalated = True
                    auto_escalated.append(record)
                    logger.warning(
                        f"Auto-escalation: {escalation_id} from "
                        f"Tier {current.value} to Tier {new_tier.value} "
                        f"(SLA breached after {elapsed:.0f}s)"
                    )

        return auto_escalated

    def get_active_escalations(self) -> List[EscalationRecord]:
        return list(self._active_escalations.values())

    def get_resolved_escalations(self) -> List[EscalationRecord]:
        return self._resolved_escalations

    def get_escalation_stats(self) -> Dict[str, Any]:
        active_by_tier = {}
        for record in self._active_escalations.values():
            tier = record.current_tier.value
            active_by_tier[f"tier_{tier}"] = active_by_tier.get(f"tier_{tier}", 0) + 1

        decisions = {}
        for record in self._resolved_escalations:
            d = record.decision or "pending"
            decisions[d] = decisions.get(d, 0) + 1

        return {
            "active_escalations": len(self._active_escalations),
            "resolved_escalations": len(self._resolved_escalations),
            "active_by_tier": active_by_tier,
            "resolution_decisions": decisions,
        }
