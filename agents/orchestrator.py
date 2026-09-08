"""
Central Orchestrator — LangGraph State Graph

The core multi-agent workflow engine that coordinates:
1. Signal intake (transactions, communications, regulatory changes)
2. Agent dispatch and parallel execution
3. Consensus resolution
4. Escalation decisions
5. Report generation
6. Audit trail maintenance

Architecture: LangGraph StateGraph with conditional routing.
Uses a hierarchical topology — orchestrator manages the four specialist agents.
"""

import json
import os
import sys
import time
import logging
from typing import Any, Dict, List, Optional, Literal, TypedDict
from datetime import datetime, timezone

from langgraph.graph import StateGraph, END

from agents.transaction_monitor import TransactionMonitor
from agents.communication_scanner import CommunicationScanner
from agents.regulatory_tracker import RegulatoryTracker
from agents.report_generator import ReportGenerator
from consensus.resolver import ConsensusEngine
from escalation.framework import EscalationFramework
from observability.logger import get_structured_logger, Severity, LogCategory
from observability.audit_trail import get_audit_trail
from observability.dashboard import ComplianceDashboard, AgentStatus, DetectionRecord
from protocols.message_schema import (
    AgentID, AlertSeverity, ViolationType,
    MessageEnvelope, MessageType, Priority, AuditClassification,
)

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# State Definition
# ---------------------------------------------------------------------------

class ComplianceState(TypedDict):
    """State flowing through the orchestration graph."""
    # Input
    scenario_id: str
    input_data: Dict[str, Any]
    context: Dict[str, Any]

    # Agent outputs
    tm_detections: List[Dict[str, Any]]
    cs_detections: List[Dict[str, Any]]
    ru_detections: List[Dict[str, Any]]

    # Combined detections
    all_detections: List[Dict[str, Any]]

    # Consensus
    agent_assessments: Dict[str, Dict[str, Any]]
    consensus_result: Dict[str, Any]

    # Escalation
    escalation: Optional[Dict[str, Any]]
    escalation_decision: Optional[Dict[str, Any]]

    # Report
    reports: Dict[str, Dict[str, Any]]

    # Audit
    audit_entries: List[Dict[str, Any]]
    messages: List[Dict[str, Any]]

    # Metadata
    start_time: float
    tool_call_count: int
    error_log: List[str]
    meta: Dict[str, Any]


# ---------------------------------------------------------------------------
# Orchestrator
# ---------------------------------------------------------------------------

class ComplianceOrchestrator:
    """
    Central orchestrator managing the multi-agent compliance workflow.

    Uses LangGraph StateGraph for deterministic execution flow
    with conditional routing.
    """

    def __init__(self):
        self.tm = TransactionMonitor()
        self.cs = CommunicationScanner()
        self.ru = RegulatoryTracker()
        self.rg = ReportGenerator()
        self.consensus_engine = ConsensusEngine(prior=0.3)  # P(H) = 0.3 per consensus spec
        self.escalation_framework = EscalationFramework()
        self._log = get_structured_logger()
        self._audit = get_audit_trail()
        self._dashboard = ComplianceDashboard()

    def build_graph(self) -> StateGraph:
        """Build the LangGraph orchestration graph."""
        graph = StateGraph(ComplianceState)

        # Nodes
        graph.add_node("intake", self._node_intake)
        graph.add_node("run_agents", self._node_run_agents)
        graph.add_node("build_assessments", self._node_build_assessments)
        graph.add_node("consensus", self._node_consensus)
        graph.add_node("decide_escalation", self._node_decide_escalation)
        graph.add_node("generate_reports", self._node_generate_reports)
        graph.add_node("finalize", self._node_finalize)

        # Edges
        graph.set_entry_point("intake")
        graph.add_edge("intake", "run_agents")
        graph.add_edge("run_agents", "build_assessments")
        graph.add_edge("build_assessments", "consensus")
        graph.add_edge("consensus", "decide_escalation")
        graph.add_conditional_edges(
            "decide_escalation",
            self._should_escalate,
            {
                "escalate": "generate_reports",
                "no_escalation": "generate_reports",
            },
        )
        graph.add_edge("generate_reports", "finalize")
        graph.add_edge("finalize", END)

        return graph

    def run_scenario(
        self,
        scenario_id: str,
        input_data: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Run a complete compliance scenario through the full pipeline.

        Args:
            scenario_id: e.g. "CS-01"
            input_data: {transactions: [], communications: [], regulatory_updates: []}
            context: Additional context for detection

        Returns:
            Complete results with detections, consensus, escalation, reports, audit trail
        """
        graph = self.build_graph()
        app = graph.compile()

        initial_state: ComplianceState = {
            "scenario_id": scenario_id,
            "input_data": input_data,
            "context": context or {},
            "tm_detections": [],
            "cs_detections": [],
            "ru_detections": [],
            "all_detections": [],
            "agent_assessments": {},
            "consensus_result": {},
            "escalation": None,
            "escalation_decision": None,
            "reports": {},
            "audit_entries": [],
            "messages": [],
            "start_time": time.time(),
            "tool_call_count": 0,
            "error_log": [],
            "meta": {},
        }

        final_state = app.invoke(initial_state)

        # Build final result
        elapsed = time.time() - final_state["start_time"]
        final_state["meta"] = {
            "scenario_id": scenario_id,
            "elapsed_seconds": round(elapsed, 2),
            "total_detections": len(final_state["all_detections"]),
            "consensus_decision": final_state["consensus_result"].get("final_decision", "unknown"),
            "escalated": final_state["escalation"] is not None,
            "report_count": len(final_state["reports"]),
            "audit_entries": len(final_state["audit_entries"]),
            "error_count": len(final_state["error_log"]),
        }

        return final_state

    # -----------------------------------------------------------------------
    # Graph Nodes
    # -----------------------------------------------------------------------

    def _node_intake(self, state: ComplianceState) -> ComplianceState:
        """Node 1: Intake — log the incoming scenario and initialize trace."""
        trace_id = f"trace-{state['scenario_id']}-{int(time.time())}"

        self._log.log(
            LogCategory.AGENT_LIFECYCLE, Severity.INFO, AgentID.ORCHESTRATOR.value,
            "scenario.started", f"Scenario {state['scenario_id']} started",
            trace_id=trace_id,
        )

        self._audit.append(
            agent_id=AgentID.ORCHESTRATOR.value,
            event_type="scenario.started",
            category=LogCategory.AGENT_LIFECYCLE.value,
            severity=Severity.INFO.value,
            message=f"Scenario {state['scenario_id']} initiated",
            trace_id=trace_id,
        )

        state["messages"].append({
            "type": "intake",
            "scenario_id": state["scenario_id"],
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "trace_id": trace_id,
        })

        return state

    def _node_run_agents(self, state: ComplianceState) -> ComplianceState:
        """Node 2: Run agents — dispatch to TM, CS, RU in parallel."""
        scenario_id = state["scenario_id"]
        input_data = state["input_data"]
        context = state["context"]

        # Run Transaction Monitor
        transactions = input_data.get("transactions", [])
        if transactions or context.get("tm_signals"):
            try:
                state["tm_detections"] = self.tm.analyze_transaction_batch(
                    transactions, scenario_id=scenario_id, context=context
                )
                state["tool_call_count"] += 1
            except Exception as e:
                state["error_log"].append(f"TM error: {e}")

        # Run Communication Scanner
        communications = input_data.get("communications", [])
        if communications or context.get("cs_signals"):
            try:
                state["cs_detections"] = self.cs.scan_communications(
                    communications, scenario_id=scenario_id, context=context
                )
                state["tool_call_count"] += 1
            except Exception as e:
                state["error_log"].append(f"CS error: {e}")

        # Run Regulatory Update Tracker
        updates = input_data.get("regulatory_updates", [])
        if updates or context.get("ru_signals"):
            try:
                state["ru_detections"] = self.ru.analyze_regulatory_updates(
                    updates, scenario_id=scenario_id, context=context
                )
                state["tool_call_count"] += 1
            except Exception as e:
                state["error_log"].append(f"RU error: {e}")

        # Combine all detections
        state["all_detections"] = (
            state["tm_detections"] + state["cs_detections"] + state["ru_detections"]
        )

        # Handle false positive scenarios (CS-18)
        if context.get("is_false_positive"):
            fp_data = context.get("fp_verification", {})
            tm = TransactionMonitor()
            state["all_detections"] = [
                tm.check_false_positive(det, fp_data)
                if det.get("agent_id") == AgentID.TRANSACTION_MONITOR.value else det
                for det in state["all_detections"]
            ]
            # Remove any that became NO_ALERT
            state["all_detections"] = [
                det for det in state["all_detections"]
                if det.get("severity") != AlertSeverity.NO_ALERT.value
            ]
            state["tm_detections"] = [
                det for det in state["tm_detections"]
                if det.get("severity") != AlertSeverity.NO_ALERT.value
            ]

        # Log audit entries for each detection
        for det in state["all_detections"]:
            entry = self._audit.append(
                agent_id=det.get("agent_id", "unknown"),
                event_type=f"detection.{det.get('violation_type', 'unknown')}",
                category=LogCategory.DETECTION_EVENT.value,
                severity=det.get("severity", "MEDIUM"),
                message=det.get("description", ""),
            )
            state["audit_entries"].append({
                "sequence": entry.sequence_number,
                "event_type": entry.event_type,
            })

        return state

    def _node_build_assessments(self, state: ComplianceState) -> ComplianceState:
        """Node 3: Build agent assessments for consensus resolution."""
        agent_assessments = {}

        # Process TM detections
        if state["tm_detections"]:
            best_tm = max(state["tm_detections"], key=lambda d: d.get("confidence", 0))
            agent_assessments["TM-001"] = {
                "detected": True,
                "confidence": best_tm.get("confidence", 0.5),
                "severity": best_tm.get("severity", "MEDIUM"),
                "violation_type": best_tm.get("violation_type", "unknown"),
                "description": best_tm.get("description", ""),
                "evidence": best_tm.get("evidence", []),
            }
        else:
            agent_assessments["TM-001"] = {
                "detected": False,
                "confidence": 0.3,
                "severity": "LOW",
                "violation_type": "none",
                "description": "No transaction anomalies detected",
            }

        # Process CS detections
        if state["cs_detections"]:
            best_cs = max(state["cs_detections"], key=lambda d: d.get("confidence", 0))
            agent_assessments["CS-001"] = {
                "detected": True,
                "confidence": best_cs.get("confidence", 0.5),
                "severity": best_cs.get("severity", "MEDIUM"),
                "violation_type": best_cs.get("violation_type", "unknown"),
                "description": best_cs.get("description", ""),
                "evidence": best_cs.get("evidence", []),
            }
        else:
            agent_assessments["CS-001"] = {
                "detected": False,
                "confidence": 0.3,
                "severity": "LOW",
                "violation_type": "none",
                "description": "No communication violations detected",
            }

        # Process RU detections
        if state["ru_detections"]:
            best_ru = max(state["ru_detections"], key=lambda d: d.get("confidence", 0))
            agent_assessments["RU-001"] = {
                "detected": True,
                "confidence": best_ru.get("confidence", 0.5),
                "severity": best_ru.get("severity", "MEDIUM"),
                "violation_type": best_ru.get("violation_type", "unknown"),
                "description": best_ru.get("description", ""),
                "evidence": best_ru.get("evidence", []),
            }
        else:
            agent_assessments["RU-001"] = {
                "detected": False,
                "confidence": 0.3,
                "severity": "LOW",
                "violation_type": "none",
                "description": "No regulatory updates requiring action",
            }

        state["agent_assessments"] = agent_assessments
        return state

    def _node_consensus(self, state: ComplianceState) -> ComplianceState:
        """Node 4: Run consensus engine to resolve agent assessments."""
        result = self.consensus_engine.compute_consensus(
            agent_assessments=state["agent_assessments"],
        )
        state["consensus_result"] = {
            "final_decision": result.final_decision,
            "severity": result.severity,
            "overall_confidence": result.overall_confidence,
            "bayesian_posterior": result.bayesian_posterior,
            "ds_belief_violation": result.ds_belief_violation,
            "ds_uncertainty": result.ds_uncertainty,
            "conflict_level": result.conflict_level,
            "num_agents_reporting": result.num_agents_reporting,
            "resolution_method": result.resolution_method,
        }

        # Log consensus
        self._audit.append(
            agent_id=AgentID.ORCHESTRATOR.value,
            event_type="consensus.reached",
            category=LogCategory.DETECTION_EVENT.value,
            severity=Severity.INFO.value,
            message=f"Consensus: {result.final_decision} (confidence: {result.overall_confidence:.2f})",
            payload=state["consensus_result"],
        )

        return state

    def _node_decide_escalation(self, state: ComplianceState) -> ComplianceState:
        """Node 5: Decide whether to escalate to human review."""
        consensus = state["consensus_result"]
        # Escalate if ANY agent detected with high confidence, or if consensus agrees
        any_agent_detected = any(
            a.get("detected", False) and a.get("confidence", 0) > 0.7
            for a in state["agent_assessments"].values()
        )
        should_escalate = (
            consensus.get("final_decision") == "detect"
            or any_agent_detected
        ) and len(state["all_detections"]) > 0

        if should_escalate and state["all_detections"]:
            # Create escalation
            best_detection = max(
                state["all_detections"],
                key=lambda d: d.get("confidence", 0)
            )

            escalation = self.escalation_framework.create_escalation(
                detection_id=state["scenario_id"],
                detection_data=best_detection,
                agent_assessments=state["agent_assessments"],
                consensus_result=consensus,
            )

            state["escalation"] = {
                "escalation_id": escalation.escalation_id,
                "current_tier": escalation.current_tier.value,
                "triggered_by": [t.value for t in escalation.triggered_by],
                "sla_deadline": escalation.decision_support.detection_summary.get("sla_deadline", ""),
                "recommended_actions": escalation.decision_support.recommended_actions,
            }

            # Log escalation
            self._audit.append(
                agent_id=AgentID.ORCHESTRATOR.value,
                event_type="escalation.created",
                category=LogCategory.ESCALATION_EVENT.value,
                severity=Severity.ALERT.value,
                message=f"Escalation {escalation.escalation_id} created at Tier {escalation.current_tier.value}",
                payload=state["escalation"],
            )

        return state

    def _should_escalate(self, state: ComplianceState) -> Literal["escalate", "no_escalation"]:
        """Conditional edge: determine if escalation occurred."""
        if state["escalation"]:
            return "escalate"
        return "no_escalation"

    def _node_generate_reports(self, state: ComplianceState) -> ComplianceState:
        """Node 6: Generate reports for each target audience."""
        audiences = ["operations", "management", "board", "regulator", "auditor"]

        for audience in audiences:
            try:
                report = self.rg.generate_detection_report(
                    detections=state["all_detections"],
                    consensus_result=state["consensus_result"],
                    escalation=state["escalation"],
                    audit_trail_entries=state["audit_entries"],
                    audience=audience,
                    scenario_id=state["scenario_id"],
                )
                state["reports"][audience] = {
                    "report_id": report.get("report_id", ""),
                    "sections": list(report.get("sections", {}).keys()),
                }
            except Exception as e:
                state["error_log"].append(f"Report generation error ({audience}): {e}")

        return state

    def _node_finalize(self, state: ComplianceState) -> ComplianceState:
        """Node 7: Finalize — log completion and update dashboard."""
        elapsed = time.time() - state["start_time"]

        self._audit.append(
            agent_id=AgentID.ORCHESTRATOR.value,
            event_type="scenario.completed",
            category=LogCategory.AGENT_LIFECYCLE.value,
            severity=Severity.INFO.value,
            message=f"Scenario {state['scenario_id']} completed in {elapsed:.2f}s",
        )

        # Update dashboard
        for det in state["all_detections"]:
            self._dashboard.record_detection(DetectionRecord(
                violation_type=det.get("violation_type", ""),
                severity=det.get("severity", ""),
                agent_id=det.get("agent_id", ""),
                confidence=det.get("confidence", 0),
                timestamp=datetime.now(timezone.utc).isoformat(),
                time_to_detection_ms=det.get("detection_latency_ms", 0),
            ))

        if state["escalation"]:
            self._dashboard.record_escalation(state["escalation"])

        return state


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

_orchestrator: Optional[ComplianceOrchestrator] = None


def get_orchestrator() -> ComplianceOrchestrator:
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = ComplianceOrchestrator()
    return _orchestrator


def run_scenario(
    scenario_id: str,
    input_data: Dict[str, Any],
    context: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """High-level entry point to run a compliance scenario."""
    orchestrator = get_orchestrator()
    return orchestrator.run_scenario(scenario_id, input_data, context)
