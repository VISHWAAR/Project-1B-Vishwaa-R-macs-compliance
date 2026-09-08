"""
Monitoring Dashboard — 3-Panel Architecture

Panel 1: System Health (Target: Operations Team)
  - Agent status (running, degraded, stopped)
  - Message queue depths with alert thresholds
  - Processing latency percentiles (P50, P95, P99)
  - Resource utilisation (CPU, memory)
  - Error rates with trend analysis

Panel 2: Compliance Effectiveness (Target: Compliance Leadership)
  - Detection rate by violation type
  - False positive rate by agent
  - Time-to-detection distribution
  - Time-to-escalation and time-to-resolution
  - Regulatory filing accuracy

Panel 3: Operational Intelligence (Target: Senior Management)
  - Escalation volume and distribution
  - Human decision patterns
  - Agent conflict frequency
  - Cost-per-detection metrics
"""

import time
from collections import defaultdict
from datetime import datetime, timezone, timedelta
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field


@dataclass
class AgentStatus:
    agent_id: str
    status: str = "running"  # running, degraded, stopped
    heartbeat_at: str = ""
    uptime_seconds: float = 0.0
    queue_depth: int = 0
    error_rate: float = 0.0
    latency_p50_ms: float = 0.0
    latency_p95_ms: float = 0.0
    latency_p99_ms: float = 0.0


@dataclass
class DetectionRecord:
    violation_type: str
    severity: str
    agent_id: str
    confidence: float
    timestamp: str
    is_false_positive: bool = False
    time_to_detection_ms: float = 0.0
    escalated: bool = False
    time_to_escalation_ms: float = 0.0
    resolved: bool = False
    time_to_resolution_ms: float = 0.0


class ComplianceDashboard:
    """Three-panel compliance monitoring dashboard."""

    def __init__(self):
        self._agent_statuses: Dict[str, AgentStatus] = {}
        self._detections: List[DetectionRecord] = []
        self._escalations: List[Dict[str, Any]] = []
        self._conflicts: List[Dict[str, Any]] = []
        self._human_decisions: List[Dict[str, Any]] = []
        self._start_time = time.time()

    # -- Agent Status --

    def update_agent_status(self, agent_id: str, status: AgentStatus):
        self._agent_statuses[agent_id] = status

    # -- Detection Recording --

    def record_detection(self, record: DetectionRecord):
        self._detections.append(record)

    def record_escalation(self, escalation: Dict[str, Any]):
        self._escalations.append(escalation)

    def record_conflict(self, conflict: Dict[str, Any]):
        self._conflicts.append(conflict)

    def record_human_decision(self, decision: Dict[str, Any]):
        self._human_decisions.append(decision)

    # -- Panel 1: System Health --

    def get_system_health_panel(self) -> Dict[str, Any]:
        """System Health Panel — for Operations Team."""
        queue_thresholds = {"warning": 0.80, "critical": 0.95}
        max_queue = 1000

        agent_details = []
        for agent_id, status in self._agent_statuses.items():
            queue_util = status.queue_depth / max_queue if max_queue > 0 else 0
            agent_details.append({
                "agent_id": agent_id,
                "status": status.status,
                "uptime_seconds": round(status.uptime_seconds, 1),
                "queue_depth": status.queue_depth,
                "queue_utilization": round(queue_util, 3),
                "queue_alert": (
                    "critical" if queue_util >= queue_thresholds["critical"]
                    else "warning" if queue_util >= queue_thresholds["warning"]
                    else "normal"
                ),
                "error_rate": round(status.error_rate, 4),
                "latency_p50_ms": round(status.latency_p50_ms, 2),
                "latency_p95_ms": round(status.latency_p95_ms, 2),
                "latency_p99_ms": round(status.latency_p99_ms, 2),
            })

        running = sum(1 for a in agent_details if a["status"] == "running")
        total = len(agent_details)

        return {
            "panel": "System Health",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "system_status": "healthy" if running == total else "degraded",
            "agents_running": f"{running}/{total}",
            "agent_details": agent_details,
            "uptime_seconds": round(time.time() - self._start_time, 1),
        }

    # -- Panel 2: Compliance Effectiveness --

    def get_compliance_effectiveness_panel(self) -> Dict[str, Any]:
        """Compliance Effectiveness Panel — for Compliance Leadership."""
        if not self._detections:
            return {
                "panel": "Compliance Effectiveness",
                "total_detections": 0,
                "message": "No detections recorded yet",
            }

        # Detection rates by violation type
        by_violation = defaultdict(int)
        by_agent = defaultdict(int)
        false_positives = 0
        detection_latencies = []

        for d in self._detections:
            by_violation[d.violation_type] += 1
            by_agent[d.agent_id] += 1
            if d.is_false_positive:
                false_positives += 1
            if d.time_to_detection_ms > 0:
                detection_latencies.append(d.time_to_detection_ms)

        # Escalation metrics
        escalation_latencies = [e.get("time_ms", 0) for e in self._escalations if e.get("time_ms")]
        resolution_latencies = [
            d.time_to_resolution_ms for d in self._detections if d.resolved and d.time_to_resolution_ms > 0
        ]

        total = len(self._detections)
        fp_rate = false_positives / total if total > 0 else 0

        return {
            "panel": "Compliance Effectiveness",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "total_detections": total,
            "false_positive_rate": round(fp_rate, 4),
            "detections_by_violation": dict(by_violation),
            "detections_by_agent": dict(by_agent),
            "avg_detection_latency_ms": round(
                sum(detection_latencies) / len(detection_latencies), 2
            ) if detection_latencies else 0,
            "avg_escalation_latency_ms": round(
                sum(escalation_latencies) / len(escalation_latencies), 2
            ) if escalation_latencies else 0,
            "avg_resolution_latency_ms": round(
                sum(resolution_latencies) / len(resolution_latencies), 2
            ) if resolution_latencies else 0,
        }

    # -- Panel 3: Operational Intelligence --

    def get_operational_intelligence_panel(self) -> Dict[str, Any]:
        """Operational Intelligence Panel — for Senior Management."""
        escalation_by_tier = defaultdict(int)
        escalation_by_type = defaultdict(int)
        for e in self._escalations:
            escalation_by_tier[f"tier_{e.get('tier', '?')}"] += 1
            escalation_by_type[e.get("type", "unknown")] += 1

        conflict_types = defaultdict(int)
        for c in self._conflicts:
            conflict_types[c.get("type", "unknown")] += 1

        human_approvals = sum(1 for d in self._human_decisions if d.get("decision") == "approve")
        human_overrides = sum(1 for d in self._human_decisions if d.get("decision") == "override")
        total_human = len(self._human_decisions)

        return {
            "panel": "Operational Intelligence",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "escalation_summary": {
                "total_escalations": len(self._escalations),
                "by_tier": dict(escalation_by_tier),
                "by_type": dict(escalation_by_type),
            },
            "conflict_summary": {
                "total_conflicts": len(self._conflicts),
                "by_type": dict(conflict_types),
            },
            "human_decision_summary": {
                "total_decisions": total_human,
                "approval_rate": round(human_approvals / total_human, 3) if total_human > 0 else 0,
                "override_rate": round(human_overrides / total_human, 3) if total_human > 0 else 0,
            },
        }

    # -- Full Dashboard --

    def get_full_dashboard(self) -> Dict[str, Any]:
        """Get all three panels combined."""
        return {
            "system_health": self.get_system_health_panel(),
            "compliance_effectiveness": self.get_compliance_effectiveness_panel(),
            "operational_intelligence": self.get_operational_intelligence_panel(),
        }

    def generate_summary_markdown(self) -> str:
        """Generate a markdown summary of the dashboard."""
        health = self.get_system_health_panel()
        compliance = self.get_compliance_effectiveness_panel()
        ops = self.get_operational_intelligence_panel()

        lines = [
            "# Compliance Monitoring Dashboard",
            f"\n**Generated:** {datetime.now(timezone.utc).isoformat()}",
            f"\n## Panel 1: System Health",
            f"- **Status:** {health.get('system_status', 'unknown')}",
            f"- **Agents Running:** {health.get('agents_running', 'N/A')}",
            f"- **Uptime:** {health.get('uptime_seconds', 0):.0f}s",
        ]

        for agent in health.get("agent_details", []):
            alert_icon = "🔴" if agent["queue_alert"] == "critical" else ("🟡" if agent["queue_alert"] == "warning" else "🟢")
            lines.append(f"  - {alert_icon} **{agent['agent_id']}**: {agent['status']} "
                        f"(queue: {agent['queue_depth']}, errors: {agent['error_rate']:.2%})")

        lines.extend([
            f"\n## Panel 2: Compliance Effectiveness",
            f"- **Total Detections:** {compliance.get('total_detections', 0)}",
            f"- **False Positive Rate:** {compliance.get('false_positive_rate', 0):.2%}",
            f"- **Avg Detection Latency:** {compliance.get('avg_detection_latency_ms', 0):.0f}ms",
        ])

        by_violation = compliance.get("detections_by_violation", {})
        if by_violation:
            lines.append("\n**Detections by Type:**")
            for vtype, count in sorted(by_violation.items(), key=lambda x: -x[1]):
                lines.append(f"  - {vtype}: {count}")

        lines.extend([
            f"\n## Panel 3: Operational Intelligence",
            f"- **Total Escalations:** {ops.get('escalation_summary', {}).get('total_escalations', 0)}",
            f"- **Total Conflicts:** {ops.get('conflict_summary', {}).get('total_conflicts', 0)}",
            f"- **Human Decisions:** {ops.get('human_decision_summary', {}).get('total_decisions', 0)}",
        ])

        return "\n".join(lines)
# Dashboard update
