# Monitoring Dashboard

## Overview

The monitoring dashboard provides a 3-panel view of system health, compliance effectiveness, and operational intelligence. It is designed for three distinct audiences: Operations Team, Compliance Leadership, and Senior Management.

**Module:** `observability/dashboard.py`  
**Class:** `ComplianceDashboard`  
**Data Classes:** `AgentStatus`, `DetectionRecord`

## Panel Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                 COMPLIANCE MONITORING DASHBOARD              │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────────────┐  ┌─────────────────────┐         │
│  │ PANEL 1: SYSTEM     │  │ PANEL 2: COMPLIANCE  │         │
│  │ HEALTH              │  │ EFFECTIVENESS        │         │
│  │ (Operations Team)   │  │ (Compliance Leaders) │         │
│  │                     │  │                      │         │
│  │ - Agent status      │  │ - Detection rate by  │         │
│  │ - Queue depths      │  │   violation type     │         │
│  │ - Latency P50/P95/  │  │ - False positive rate│         │
│  │   P99               │  │ - Time-to-detection  │         │
│  │ - Error rates       │  │ - Time-to-escalation │         │
│  │ - Resource usage    │  │ - Time-to-resolution │         │
│  └─────────────────────┘  │ - Filing accuracy    │         │
│                            └─────────────────────┘         │
│                            ┌─────────────────────┐         │
│                            │ PANEL 3: OPERATIONAL │         │
│                            │ INTELLIGENCE         │         │
│                            │ (Senior Management)  │         │
│                            │                      │         │
│                            │ - Escalation volume  │         │
│                            │ - Human decision     │         │
│                            │   patterns           │         │
│                            │ - Agent conflict     │         │
│                            │   frequency          │         │
│                            │ - Cost-per-detection │         │
│                            └─────────────────────┘         │
└─────────────────────────────────────────────────────────────┘
```

## Panel 1: System Health

**Target Audience:** Operations Team

### Metrics

| Metric | Description |
|--------|-------------|
| `system_status` | "healthy" if all agents running, "degraded" otherwise |
| `agents_running` | "X/Y" format (running/total) |
| `agent_details[]` | Per-agent: status, uptime, queue depth, queue utilization, queue alert level, error rate, P50/P95/P99 latency |
| `uptime_seconds` | Total system uptime since dashboard creation |

### Queue Alert Levels

| Utilization | Alert |
|-------------|-------|
| < 80% | normal (green) |
| 80-95% | warning (yellow) |
| ≥ 95% | critical (red) |

### AgentStatus Structure

```python
@dataclass
class AgentStatus:
    agent_id: str
    status: str                    # "running", "degraded", "stopped"
    heartbeat_at: str              # Last heartbeat timestamp
    uptime_seconds: float          # Seconds since agent start
    queue_depth: int               # Pending items in agent queue
    error_rate: float              # Error rate over measurement window
    latency_p50_ms: float          # 50th percentile latency
    latency_p95_ms: float          # 95th percentile latency
    latency_p99_ms: float          # 99th percentile latency
```

## Panel 2: Compliance Effectiveness

**Target Audience:** Compliance Leadership

### Metrics

| Metric | Description |
|--------|-------------|
| `total_detections` | Total detection events recorded |
| `false_positive_rate` | FP / total detections |
| `detections_by_violation` | Count per violation type |
| `detections_by_agent` | Count per agent |
| `avg_detection_latency_ms` | Average time from event to detection |
| `avg_escalation_latency_ms` | Average time from detection to escalation |
| `avg_resolution_latency_ms` | Average time from escalation to resolution |

### DetectionRecord Structure

```python
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
```

## Panel 3: Operational Intelligence

**Target Audience:** Senior Management

### Metrics

| Metric | Description |
|--------|-------------|
| `escalation_summary.total_escalations` | Total escalations (active + resolved) |
| `escalation_summary.by_tier` | Escalations per tier |
| `escalation_summary.by_type` | Escalations per type |
| `conflict_summary.total_conflicts` | Total inter-agent conflicts recorded |
| `conflict_summary.by_type` | Conflicts per type |
| `human_decision_summary.total_decisions` | Total human decisions recorded |
| `human_decision_summary.approval_rate` | Approvals / total decisions |
| `human_decision_summary.override_rate` | Overrides / total decisions |

## Full Dashboard Access

```python
dashboard = ComplianceDashboard()

# Get all three panels
full = dashboard.get_full_dashboard()
# Returns: {system_health, compliance_effectiveness, operational_intelligence}

# Get markdown summary (human-readable)
md = dashboard.generate_summary_markdown()
# Returns formatted markdown with all panels
```

## Recording Events

```python
# Record a detection
dashboard.record_detection(DetectionRecord(
    violation_type="INSIDER_TRADING",
    severity="CRITICAL",
    agent_id="TM-001",
    confidence=0.85,
    timestamp="2026-09-01T10:00:00Z",
    time_to_detection_ms=45.2,
))

# Record an escalation
dashboard.record_escalation({
    "escalation_id": "ESC-000001",
    "tier": 3,
    "type": "CRITICAL_SEVERITY",
    "time_ms": 1200,
})

# Record a conflict
dashboard.record_conflict({
    "type": "severity_disagreement",
    "agents": ["TM-001", "CS-001"],
})

# Record a human decision
dashboard.record_human_decision({
    "decision_id": "DEC-000001",
    "decision": "approve",
    "rationale": "Investigation confirmed insider trading pattern",
})
```

## Integration

The dashboard is updated by the orchestrator's `_node_finalize` method after each scenario completes. Detection records and escalation records are recorded from the scenario result state.

## Implementation

See `observability/dashboard.py` — `ComplianceDashboard`, `AgentStatus`, `DetectionRecord`, all `get_*_panel()` methods, `record_*` methods, `generate_summary_markdown()`.
