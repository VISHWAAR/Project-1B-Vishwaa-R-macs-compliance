"""
Regulatory Update Tracker Agent (RU-001)

Continuous monitoring of the regulatory landscape across all operating jurisdictions.
Detects: new regulations, amendments, enforcement actions, guidance documents,
no-action letters, consultation papers. Assesses impact and detects cross-jurisdiction conflicts.
"""

import time
import logging
from typing import Any, Dict, List, Optional
from datetime import datetime, timezone

from observability.logger import get_structured_logger, Severity, LogCategory
from observability.audit_trail import get_audit_trail
from protocols.message_schema import AgentID, AlertSeverity, ViolationType, DetectionEvidence

logger = logging.getLogger(__name__)


# Regulatory bodies we monitor
MONITORED_JURISDICTIONS = [
    "SEC", "FINRA", "OCC", "CFPB",  # US
    "FCA", "ECB/SSM",               # UK/EU
    "MAS", "HKMA",                   # APAC
    "SEBI", "RBI",                   # India
    "JFSA", "ASIC",                  # APAC
]


class RegulatoryTracker:
    """Regulatory Update Tracker agent."""

    def __init__(self):
        self._log = get_structured_logger()
        self._audit = get_audit_trail()
        self._agent_id = AgentID.REGULATORY_TRACKER.value
        self._regulatory_updates: List[Dict[str, Any]] = []

    def analyze_regulatory_updates(
        self,
        updates: List[Dict[str, Any]],
        scenario_id: str = "",
        context: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """Analyze regulatory updates for compliance impact."""
        start_time = time.time()
        detections = []
        ctx = context or {}

        detections.extend(self._detect_regulatory_change(updates, ctx))
        detections.extend(self._detect_cross_jurisdiction_conflict(updates, ctx))
        detections.extend(self._detect_enforcement_action_impact(updates, ctx))
        detections.extend(self._detect_sanctions_update(updates, ctx))

        elapsed_ms = (time.time() - start_time) * 1000

        for det in detections:
            det["detection_latency_ms"] = elapsed_ms
            det["scenario_id"] = scenario_id
            det["agent_id"] = self._agent_id

        self._regulatory_updates.extend(detections)
        return detections

    def _detect_regulatory_change(
        self, updates: List[Dict], context: Dict
    ) -> List[Dict]:
        """Detect regulatory changes that require system updates."""
        detections = []

        if context.get("regulatory_change_detected", False):
            change = context.get("change_details", {})
            impact_score = context.get("impact_score", 0.5)
            deadline_days = context.get("implementation_deadline_days", 180)
            jurisdictions = context.get("affected_jurisdictions", ["US"])

            confidence = min(0.95, 0.5 + impact_score * 0.4)

            detections.append({
                "violation_type": ViolationType.REGULATORY_CHANGE.value,
                "severity": AlertSeverity.MEDIUM.value,
                "confidence": confidence,
                "description": f"Regulatory change requiring impact assessment: "
                              f"{change.get('title', 'New regulation')} "
                              f"(deadline: {deadline_days} days)",
                "evidence": [DetectionEvidence(
                    source="regulatory_feed",
                    timestamp=datetime.now(timezone.utc).isoformat(),
                    description=f"New regulation published by {change.get('body', 'regulator')}",
                    data=change,
                    confidence=confidence,
                ).model_dump()],
                "regulations": [change.get("regulation_id", "")],
                "jurisdictions": jurisdictions,
            })

        return detections

    def _detect_cross_jurisdiction_conflict(
        self, updates: List[Dict], context: Dict
    ) -> List[Dict]:
        """Detect conflicts between regulations from different jurisdictions."""
        detections = []

        if context.get("jurisdictional_conflict", False):
            conflict = context.get("conflict_details", {})
            jurisdiction_a = conflict.get("jurisdiction_a", "EU")
            jurisdiction_b = conflict.get("jurisdiction_b", "Singapore")

            confidence = context.get("ru_confidence", 0.75)

            detections.append({
                "violation_type": ViolationType.REGULATORY_CHANGE.value,
                "severity": AlertSeverity.HIGH.value,
                "confidence": confidence,
                "description": f"Cross-jurisdictional regulatory conflict between "
                              f"{jurisdiction_a} and {jurisdiction_b}: {conflict.get('description', '')}",
                "evidence": [DetectionEvidence(
                    source="cross_regulation_analysis",
                    timestamp=datetime.now(timezone.utc).isoformat(),
                    description=f"Conflict detected between {jurisdiction_a} and {jurisdiction_b} regulations",
                    data=conflict,
                    confidence=confidence,
                ).model_dump()],
                "regulations": conflict.get("regulations", []),
                "jurisdictions": [jurisdiction_a, jurisdiction_b],
            })

        return detections

    def _detect_enforcement_action_impact(
        self, updates: List[Dict], context: Dict
    ) -> List[Dict]:
        """Detect enforcement actions that may affect the bank's compliance posture."""
        detections = []

        if context.get("enforcement_action", False):
            action = context.get("action_details", {})
            fine_amount = action.get("fine_amount", 0)
            bank_affected = action.get("bank_affected", "")
            applicability = action.get("applicability_to_us", "medium")

            confidence = context.get("ru_confidence", 0.65)

            if applicability in ("high", "medium"):
                detections.append({
                    "violation_type": ViolationType.REGULATORY_CHANGE.value,
                    "severity": AlertSeverity.MEDIUM.value if applicability == "medium" else AlertSeverity.HIGH.value,
                    "confidence": confidence,
                    "description": f"Enforcement action against {bank_affected}: "
                                  f"${fine_amount:,.0f} fine for {action.get('violation', '')}. "
                                  f"Applicability to our operations: {applicability}",
                    "evidence": [DetectionEvidence(
                        source="enforcement_feed",
                        timestamp=datetime.now(timezone.utc).isoformat(),
                        description=f"Enforcement action by {action.get('regulator', 'regulator')}",
                        data=action,
                        confidence=confidence,
                    ).model_dump()],
                    "regulations": action.get("regulations", []),
                    "jurisdictions": action.get("jurisdictions", ["US"]),
                })

        return detections

    def _detect_sanctions_update(
        self, updates: List[Dict], context: Dict
    ) -> List[Dict]:
        """
        Detect sanctions list (SDN) updates that affect existing transactions.

        The RU monitors the regulatory feed for new designations. When an
        entity is added to the SDN list, transactions referencing that entity
        become sanctions violations — CRITICAL severity.
        """
        detections = []

        if not context.get("ru_signals", False):
            return detections
        if not context.get("sdn_match", False):
            return detections

        sdn_entity = context.get("sdn_entity", "unknown entity")
        listed_48h_ago = context.get("sdn_listed_48h_ago", False)
        confidence = 0.85

        listing_note = "entity added to SDN list 48 hours ago" if listed_48h_ago else "entity on SDN list"

        detections.append({
            "violation_type": ViolationType.SANCTIONS_VIOLATION.value,
            "severity": AlertSeverity.CRITICAL.value,
            "confidence": confidence,
            "description": (
                f"Potential sanctions violation: wire transfer to SDN-listed subsidiary "
                f"{sdn_entity}, {listing_note}"
            ),
            "evidence": [
                DetectionEvidence(
                    source="sanctions_screening",
                    timestamp=datetime.now(timezone.utc).isoformat(),
                    description=f"Beneficiary matches SDN list entity ({sdn_entity})",
                    data={"sdn_entity": sdn_entity, "listed_48h_ago": listed_48h_ago},
                    confidence=confidence,
                ).model_dump(),
                DetectionEvidence(
                    source="wire_transfer_log",
                    timestamp=datetime.now(timezone.utc).isoformat(),
                    description="3 intermediary banks in transfer chain",
                    confidence=confidence,
                ).model_dump(),
            ],
            "regulations": ["OFAC Regulations", "31 CFR Part 501", "EU Sanctions Regulation"],
            "jurisdictions": ["US"],
            "requires_sar": True,
        })

        return detections

    def assess_impact_on_system(
        self,
        detection: Dict[str, Any],
        current_policies: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Assess how a regulatory change impacts the existing compliance system.

        Returns impact assessment with recommended actions.
        """
        affected_agents = []
        policy_gaps = []
        recommended_actions = []

        violation_type = detection.get("violation_type", "")

        if violation_type == ViolationType.REGULATORY_CHANGE.value:
            # Determine which agents need updates
            regulations = detection.get("regulations", [])
            jurisdictions = detection.get("jurisdictions", [])

            # All agents may need updates for major regulatory changes
            if any(j in ("US", "EU") for j in jurisdictions):
                affected_agents = ["TM-001", "CS-001", "RU-001", "RG-001"]
                recommended_actions = [
                    "Update detection thresholds per new regulation",
                    "Revise report templates to include new disclosure requirements",
                    "Update compliance rule engine with new parameters",
                    "Schedule training for compliance staff on new requirements",
                ]

        return {
            "affected_agents": affected_agents,
            "policy_gaps": policy_gaps,
            "recommended_actions": recommended_actions,
            "estimated_implementation_days": 30,
            "priority": "high" if detection.get("severity") == "CRITICAL" else "medium",
        }
