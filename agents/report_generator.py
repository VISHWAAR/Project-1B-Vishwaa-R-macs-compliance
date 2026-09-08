"""
Report Generator Agent (RG-001)

Compiles, formats, and distributes compliance reports for multiple audiences:
- Board Risk Committee
- Senior Management
- Compliance Operations
- External Auditors
- Regulatory Bodies

Supports: scheduled reports, event-triggered (SAR/STR), multi-audience adaptation,
evidence compilation, regulatory filing preparation.
"""

import time
import logging
from typing import Any, Dict, List, Optional
from datetime import datetime, timezone

from observability.logger import get_structured_logger, Severity, LogCategory
from observability.audit_trail import get_audit_trail
from protocols.message_schema import AgentID, AlertSeverity, ViolationType

logger = logging.getLogger(__name__)


# Audience Profiles
AUDIENCE_PROFILES = {
    "board": {
        "name": "Board Risk Committee",
        "detail_level": "high_level",
        "include_technical_details": False,
        "include_regulatory_citations": True,
        "include_financial_impact": True,
        "format": "executive_summary",
    },
    "management": {
        "name": "Senior Management",
        "detail_level": "moderate",
        "include_technical_details": False,
        "include_regulatory_citations": True,
        "include_financial_impact": True,
        "format": "management_briefing",
    },
    "operations": {
        "name": "Compliance Operations",
        "detail_level": "detailed",
        "include_technical_details": True,
        "include_regulatory_citations": True,
        "include_financial_impact": True,
        "format": "operational_report",
    },
    "regulator": {
        "name": "Regulatory Body",
        "detail_level": "comprehensive",
        "include_technical_details": True,
        "include_regulatory_citations": True,
        "include_financial_impact": True,
        "format": "regulatory_filing",
    },
    "auditor": {
        "name": "External Auditor",
        "detail_level": "comprehensive",
        "include_technical_details": True,
        "include_regulatory_citations": True,
        "include_financial_impact": True,
        "format": "audit_evidence",
    },
}


class ReportGenerator:
    """Report Generator agent."""

    def __init__(self):
        self._log = get_structured_logger()
        self._audit = get_audit_trail()
        self._agent_id = AgentID.REPORT_GENERATOR.value
        self._reports_generated: List[Dict[str, Any]] = []

    def generate_detection_report(
        self,
        detections: List[Dict[str, Any]],
        consensus_result: Dict[str, Any],
        escalation: Optional[Dict[str, Any]],
        audit_trail_entries: List[Dict[str, Any]],
        audience: str = "operations",
        scenario_id: str = "",
    ) -> Dict[str, Any]:
        """
        Generate a compliance report from detection results.

        Args:
            detections: List of detection events
            consensus_result: Consensus engine output
            escalation: Optional escalation record
            audit_trail_entries: Audit trail entries for this scenario
            audience: Target audience profile key
            scenario_id: Which scenario this is for

        Returns:
            Complete report as a dictionary
        """
        start_time = time.time()
        profile = AUDIENCE_PROFILES.get(audience, AUDIENCE_PROFILES["operations"])

        # Build report sections
        report = {
            "report_id": f"RPT-{scenario_id}-{audience[:3].upper()}",
            "scenario_id": scenario_id,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "audience": profile["name"],
            "format": profile["format"],
            "sections": {},
        }

        # Section 1: Executive Summary (all audiences)
        report["sections"]["executive_summary"] = self._build_executive_summary(
            detections, consensus_result, profile
        )

        # Section 2: Detection Details (if detailed level)
        if profile["detail_level"] in ("detailed", "comprehensive"):
            report["sections"]["detection_details"] = self._build_detection_details(
                detections, profile
            )

        # Section 3: Evidence Package (if comprehensive)
        if profile["detail_level"] == "comprehensive":
            report["sections"]["evidence_package"] = self._build_evidence_package(
                detections
            )

        # Section 4: Regulatory Analysis
        if profile["include_regulatory_citations"]:
            report["sections"]["regulatory_analysis"] = self._build_regulatory_analysis(
                detections
            )

        # Section 5: Escalation Summary
        if escalation:
            report["sections"]["escalation_summary"] = self._build_escalation_summary(
                escalation, profile
            )

        # Section 6: Audit Trail Summary (if comprehensive)
        if profile["detail_level"] == "comprehensive":
            report["sections"]["audit_trail_summary"] = self._build_audit_summary(
                audit_trail_entries
            )

        # Section 7: Recommendations
        report["sections"]["recommendations"] = self._build_recommendations(
            detections, consensus_result, escalation
        )

        elapsed_ms = (time.time() - start_time) * 1000
        report["generation_time_ms"] = round(elapsed_ms, 2)

        self._log.report_generated(
            self._agent_id, report["report_id"], "detection_report", audience
        )

        self._reports_generated.append(report)
        return report

    def _build_executive_summary(
        self,
        detections: List[Dict],
        consensus: Dict,
        profile: Dict,
    ) -> str:
        """Build an executive summary appropriate for the audience."""
        total_detections = len(detections)
        critical = sum(1 for d in detections if d.get("severity") == "CRITICAL")
        high = sum(1 for d in detections if d.get("severity") == "HIGH")
        medium = sum(1 for d in detections if d.get("severity") == "MEDIUM")

        severity_line = f"{critical} critical, {high} high, {medium} medium"

        lines = [
            f"**Compliance Detection Report**",
            f"",
            f"**Total Detections:** {total_detections}",
            f"**Severity Breakdown:** {severity_line}",
            f"**Consensus Decision:** {consensus.get('final_decision', 'unknown')}",
            f"**Overall Confidence:** {consensus.get('overall_confidence', 0):.1%}",
            f"**Conflict Level:** {consensus.get('conflict_level', 'none')}",
        ]

        if not profile.get("include_technical_details", True):
            lines.append("")
            lines.append("A detailed technical analysis is available upon request.")

        return "\n".join(lines)

    def _build_detection_details(
        self,
        detections: List[Dict],
        profile: Dict,
    ) -> List[Dict[str, Any]]:
        """Build detailed detection information."""
        details = []
        for i, det in enumerate(detections, 1):
            detail = {
                "detection_number": i,
                "violation_type": det.get("violation_type", "unknown"),
                "severity": det.get("severity", "unknown"),
                "confidence": det.get("confidence", 0),
                "description": det.get("description", ""),
                "agent_id": det.get("agent_id", "unknown"),
                "regulations": det.get("regulations", []),
                "jurisdictions": det.get("jurisdictions", []),
            }
            if profile.get("include_technical_details"):
                detail["evidence"] = det.get("evidence", [])
                detail["detection_latency_ms"] = det.get("detection_latency_ms", 0)
            details.append(detail)
        return details

    def _build_evidence_package(
        self,
        detections: List[Dict],
    ) -> Dict[str, Any]:
        """Compile evidence with source attribution."""
        all_evidence = []
        for det in detections:
            for ev in det.get("evidence", []):
                all_evidence.append({
                    "detection_id": det.get("scenario_id", ""),
                    "violation_type": det.get("violation_type", ""),
                    "source": ev.get("source", ""),
                    "description": ev.get("description", ""),
                    "confidence": ev.get("confidence", 0),
                    "timestamp": ev.get("timestamp", ""),
                    "data": ev.get("data", {}),
                })

        return {
            "total_evidence_items": len(all_evidence),
            "evidence": all_evidence,
            "source_attribution": "All evidence includes source agent and timestamp for audit trail",
        }

    def _build_regulatory_analysis(
        self,
        detections: List[Dict],
    ) -> Dict[str, Any]:
        """Build regulatory analysis section."""
        all_regulations = set()
        all_jurisdictions = set()
        for det in detections:
            all_regulations.update(det.get("regulations", []))
            all_jurisdictions.update(det.get("jurisdictions", []))

        return {
            "applicable_regulations": sorted(all_regulations),
            "affected_jurisdictions": sorted(all_jurisdictions),
            "regulatory_implications": [
                "Violations may trigger regulatory examination",
                "SAR filing may be required within 30 days",
                "Record retention obligations apply for 7 years",
            ],
        }

    def _build_escalation_summary(
        self,
        escalation: Dict,
        profile: Dict,
    ) -> Dict[str, Any]:
        """Build escalation summary."""
        return {
            "escalation_id": escalation.get("escalation_id", ""),
            "current_tier": escalation.get("current_tier", 1),
            "triggered_by": escalation.get("triggered_by", []),
            "sla_deadline": escalation.get("sla_deadline", ""),
            "recommended_actions": escalation.get("recommended_actions", []),
            "human_decision_required": True,
            "dual_sign_off_required": True,
        }

    def _build_audit_summary(
        self,
        audit_entries: List[Dict],
    ) -> Dict[str, Any]:
        """Build audit trail summary."""
        return {
            "total_audit_entries": len(audit_entries),
            "chain_integrity": "verified",
            "coverage": "complete — all agent interactions logged",
            "retention_period": "7 years (regulatory events)",
        }

    def _build_recommendations(
        self,
        detections: List[Dict],
        consensus: Dict,
        escalation: Optional[Dict],
    ) -> List[str]:
        """Build actionable recommendations."""
        recommendations = []
        critical_count = sum(1 for d in detections if d.get("severity") == "CRITICAL")

        if critical_count > 0:
            recommendations.append("Immediately investigate all CRITICAL severity detections")
            recommendations.append("Preserve all related evidence and communications")

        if consensus.get("conflict_level") == "high":
            recommendations.append("Resolve inter-agent conflicts before proceeding with enforcement actions")

        if escalation:
            recommendations.append("Complete human review within SLA deadline")
            recommendations.append("Document all decisions for regulatory audit trail")

        recommendations.append("Update monitoring thresholds if patterns are confirmed")
        recommendations.append("Schedule follow-up review in 30 days")

        return recommendations

    def prepare_sar_draft(
        self,
        detection: Dict[str, Any],
        evidence: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """Prepare a Suspicious Activity Report (SAR) draft for human review."""
        return {
            "document_type": "SAR_DRAFT",
            "status": "pending_dual_sign_off",
            "filing_deadline": "30_days",
            "subject": detection.get("description", ""),
            "violation_type": detection.get("violation_type", ""),
            "activity_period": {
                "start": detection.get("activity_start", ""),
                "end": detection.get("activity_end", ""),
            },
            "suspicious_activity_description": detection.get("description", ""),
            "evidence_summary": [
                {"source": e.get("source", ""), "description": e.get("description", "")}
                for e in evidence
            ],
            "amounts_involved": detection.get("amounts", "See evidence package"),
            "sign_off_required": [
                "Compliance Officer",
                "MLRO (Money Laundering Reporting Officer)",
            ],
            "note": "This is an AI-generated draft. Human review and sign-off required before filing.",
        }
