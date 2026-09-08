# Data Flow Architecture

## Overview

This document describes how data flows through the MACS system — from initial scenario ingestion through agent processing, consensus resolution, escalation, and report generation. It covers the complete pipeline topology, data transformation at each stage, and the message formats used for inter-agent communication.

## Pipeline Topology

```
┌──────────────────────────────────────────────────────────────────┐
│                     STAGE 0: SCENARIO INGESTION                  │
│  main.py → generate_scenario_data(scenario_id)                  │
│  Output: {input_data, context}                                  │
└───────────────────────────┬──────────────────────────────────────┘
                            │
                            ▼
┌──────────────────────────────────────────────────────────────────┐
│                     STAGE 1: INTAKE (Orchestrator Node)          │
│  - Generates trace_id: trace-{scenario_id}-{timestamp}          │
│  - Logs scenario.started event                                  │
│  - Initializes ComplianceState                                  │
│  - Appends audit entry (chain hash)                             │
└───────────────────────────┬──────────────────────────────────────┘
                            │
                            ▼
┌──────────────────────────────────────────────────────────────────┐
│                  STAGE 2: AGENT EXECUTION (Parallel)            │
│                                                                  │
│  ┌─────────────────────┐    ┌─────────────────────┐            │
│  │ Transaction Monitor  │    │ Communication       │            │
│  │ (TM-001)             │    │ Scanner (CS-001)   │            │
│  │                     │    │                     │            │
│  │ Input: transactions │    │ Input: communications│           │
│  │ Output: detections  │    │ Output: detections  │            │
│  └──────────┬──────────┘    └──────────┬──────────┘            │
│             │                           │                       │
│             └──────────┬────────────────┘                       │
│                        │                                         │
│            ┌───────────┴───────────┐                           │
│            │  Regulatory Tracker   │                           │
│            │  (RU-001)             │                           │
│            │                       │                           │
│            │ Input: regulatory_ups │                           │
│            │ Output: detections    │                           │
│            └───────────┬───────────┘                           │
│                        │                                         │
│                        ▼                                         │
│              (all detections merged)                             │
└─────────────────────────┬──────────────────────────────────────┘
                          │
                          ▼
┌──────────────────────────────────────────────────────────────────┐
│               STAGE 3: FALSE POSITIVE CHECK (CS-18 only)        │
│  - TM.check_false_positive() on each detection                  │
│  - Detections marked NO_ALERT are removed                      │
└─────────────────────────┬──────────────────────────────────────┘
                          │
                          ▼
┌──────────────────────────────────────────────────────────────────┐
│                  STAGE 4: AGENT ASSESSMENTS                      │
│  - Best detection per agent selected by max confidence          │
│  - Each agent gets {detected, confidence, severity, ...}        │
│  - Non-detecting agents get {detected: false, confidence: 0.3}  │
└─────────────────────────┬──────────────────────────────────────┘
                          │
                          ▼
┌──────────────────────────────────────────────────────────────────┐
│                  STAGE 5: CONSENSUS RESOLUTION                   │
│                                                                  │
│  ┌─────────────────────┐    ┌─────────────────────┐            │
│  │ Bayesian Consensus  │    │ Dempster-Shafer     │            │
│  │ (P(H)=0.3 prior)    │    │ (Evidence combination)            │
│  │                     │    │                     │            │
│  │ Prior: 0.3          │    │ Frame: {True, False}│           │
│  │ Likelihood per agnt │    │ Mass per agent      │            │
│  └──────────┬──────────┘    └──────────┬──────────┘            │
│             │                           │                       │
│             └───────────┬───────────────┘                       │
│                         │                                         │
│              50% Bayesian + 30% D-S + 20% max agent             │
│                         │                                         │
│                         ▼                                         │
│              Combined confidence > 0.5 → "detect"                │
│              Otherwise → "no_detect"                             │
│                                                                  │
│  Conflict Taxonomy:                                              │
│  - Type A: Severity disagreement → highest-severity resolves    │
│  - Type B: Detection disagreement → Bayesian posterior governs  │
│  - Type C: Jurisdictional conflict → RU jurisdiction wins       │
└─────────────────────────┬──────────────────────────────────────┘
                          │
                          ▼
┌──────────────────────────────────────────────────────────────────┐
│                  STAGE 6: ESCALATION DECISION                    │
│                                                                  │
│  Trigger evaluation:                                             │
│  - HIGH_CONFIDENCE_DETECTION (confidence ≥ 0.8)                │
│  - CRITICAL_SEVERITY (severity == CRITICAL)                    │
│  - MULTI_AGENT_CONFLICT (detecting + non-detecting agents)     │
│  - CROSS_JURISDICTIONAL (jurisdictions ≥ 2)                   │
│                                                                  │
│  Tier assignment:                                                │
│  - CRITICAL + cross-jurisdictional → Tier 4 (Director)        │
│  - CRITICAL → Tier 3 (Manager)                                 │
│  - HIGH or multi-agent conflict → Tier 2 (Senior Analyst)     │
│  - Default → Tier 1 (Analyst)                                  │
│                                                                  │
│  Decision Support Package built → human review packet           │
└─────────────────────────┬──────────────────────────────────────┘
                          │
                          ▼
┌──────────────────────────────────────────────────────────────────┐
│                  STAGE 7: REPORT GENERATION                      │
│  Audiences: operations, management, board, regulator, auditor   │
│  Each audience gets tailored report with appropriate detail     │
│  Reports include: executive summary, detection details,         │
│  regulatory analysis, escalation summary, evidence package,     │
│  audit trail summary, recommendations                           │
└─────────────────────────┬──────────────────────────────────────┘
                          │
                          ▼
┌──────────────────────────────────────────────────────────────────┐
│                  STAGE 8: FINALIZATION                           │
│  - scenario.completed audit entry                               │
│  - Dashboard updated with detection records                     │
│  - Escalation records recorded                                  │
└──────────────────────────────────────────────────────────────────┘
```

## Data Structures at Each Stage

### Stage 0: Input

```python
# From data/generators.py — each generate_csXX() function
{
    "input_data": {
        "transactions": [...],       # Transaction records
        "communications": [...],      # Communication records
        "regulatory_updates": [...],  # Regulatory feed items
    },
    "context": {
        "tm_signals": bool,          # Whether to run TM
        "cs_signals": bool,          # Whether to run CS
        "ru_signals": bool,          # Whether to run RU
        # ... scenario-specific context flags ...
    }
}
```

### Stage 2: Agent Detections

Each agent returns a list of detection dictionaries:

```python
{
    "violation_type": "INSIDER_TRADING",     # ViolationType enum
    "severity": "CRITICAL",                   # AlertSeverity enum
    "confidence": 0.85,                       # float 0.0-1.0
    "description": "Human-readable desc",
    "evidence": [...],                        # List of DetectionEvidence
    "regulations": ["SEC Rule 10b-5", ...],
    "jurisdictions": ["US"],
    "detection_latency_ms": 45.2,
    "agent_id": "TM-001",
}
```

### Stage 4: Agent Assessments

```python
{
    "TM-001": {
        "detected": True,
        "confidence": 0.85,
        "severity": "CRITICAL",
        "violation_type": "INSIDER_TRADING",
        "description": "...",
        "evidence": [...],
    },
    "CS-001": {
        "detected": True,
        "confidence": 0.72,
        ...
    },
    "RU-001": {
        "detected": False,
        "confidence": 0.3,
        ...
    },
}
```

### Stage 5: Consensus Result

```python
{
    "final_decision": "detect",
    "severity": "CRITICAL",
    "overall_confidence": 0.7842,
    "bayesian_posterior": 0.8125,
    "ds_belief_violation": 0.7450,
    "ds_uncertainty": 0.1523,
    "conflict_level": "low",
    "num_agents_reporting": 3,
    "resolution_method": "weighted_consensus",
}
```

### Stage 6: Escalation Record

```python
{
    "escalation_id": "ESC-000001",
    "current_tier": "TIER_3_MANAGER",
    "triggered_by": ["HIGH_CONFIDENCE_DETECTION", "CRITICAL_SEVERITY"],
    "sla_deadline": "ISO-8601-timestamp",
    "recommended_actions": [
        "Initiate immediate investigation",
        "Preserve all related communications",
        "Notify senior management within 24 hours",
    ],
}
```

### Stage 7: Report

```python
{
    "report_id": "RPT-CS-01-OPS",
    "scenario_id": "CS-01",
    "generated_at": "ISO-8601-timestamp",
    "audience": "Compliance Operations",
    "format": "operational_report",
    "sections": {
        "executive_summary": "...",
        "detection_details": [...],
        "regulatory_analysis": {...},
        "escalation_summary": {...},
        "audit_trail_summary": {...},
        "recommendations": [...],
    },
    "generation_time_ms": 12.4,
}
```

## Message Schema (Inter-Agent Communication)

All inter-agent messages conform to `MessageEnvelope` (protocols/message_schema.py):

| Field | Type | Description |
|-------|------|-------------|
| message_id | UUID v4 | Globally unique ID |
| protocol_version | string | Semantic version (1.0.0) |
| timestamp | ISO 8601 UTC | When message was created |
| sender_agent_id | AgentID | Source agent |
| recipient_agent_id | AgentID or list | Target agent(s) |
| message_type | MessageType | ALERT/QUERY/RESPONSE/UPDATE/HEARTBEAT/ESCALATION |
| priority | Priority | 1-5 with SLA mapping |
| correlation_id | string | Links related messages |
| trace_id | UUID v4 | Distributed tracing |
| payload_schema | string | Schema identifier |
| payload | dict | Message-type-specific content |
| confidence_score | float (optional) | Agent confidence 0.0-1.0 |
| ttl_seconds | int | Time-to-live |
| retry_count | int | Delivery attempts |
| audit_classification | AuditClassification | RETENTION period |
| sender_signature | string | Cryptographic signature |
| nonce | hex | Replay prevention |

### Priority → SLA Mapping

| Priority | SLA |
|----------|-----|
| CRITICAL (1) | 15 minutes |
| HIGH (2) | 1 hour |
| MEDIUM (3) | 4 hours |
| LOW (4) | 24 hours |
| INFORMATIONAL (5) | Best effort |

## False Positive Handling (CS-18)

CS-18 is the false-positive scenario: a legitimate block trade that would otherwise trigger an alert.

```
Normal detection → TM.check_false_positive(detection, fp_verification) →
  if fp_verification["is_legitimate"]:
    detection.severity = "NO_ALERT"
    detection.confidence = 0.0
    detection.is_false_positive = True
  → filtered out of all_detections
```

The context flag `is_false_positive: True` triggers this path in the orchestrator's `_node_run_agents`.

## Cross-Referenced Scenarios

| Scenario | Agents Invoked | Data Flow Path |
|----------|---------------|----------------|
| CS-01 (Insider Trading) | TM + CS | TM detects accumulation → CS provides communication link evidence → both feed consensus |
| CS-05 (Chinese Wall) | CS only | CS detects keyword breach → RU provides regulatory context → consensus |
| CS-07 (Regulatory Change) | RU only | RU detects new regulation → impact assessment → report to management |
| CS-09 (Sanctions) | TM + RU | TM flags wire to SDN entity → RU confirms SDN match → Tier 3 escalation |
| CS-18 (False Positive) | TM only | TM detects pattern → FP check clears it → NO_ALERT |
| CS-20 (Coordinated AML) | All four | TM detects structuring → CS detects comms coordination → RU confirms AML rules → all feed consensus → Tier 4 escalation |

## Error Propagation

Errors in any agent are caught and logged but do not halt the pipeline:

```python
try:
    state["tm_detections"] = self.tm.analyze_transaction_batch(...)
except Exception as e:
    state["error_log"].append(f"TM error: {e}")
    # Pipeline continues with empty detections for this agent
```

## Audit Trail Integration

Every stage produces audit trail entries via `get_audit_trail().append(...)`:

| Stage | Event Type | Category |
|-------|-----------|----------|
| Intake | scenario.started | agent_lifecycle |
| Detection | detection.{violation_type} | detection_event |
| Consensus | consensus.reached | detection_event |
| Escalation | escalation.created | escalation_event |
| Completion | scenario.completed | agent_lifecycle |

Each entry is SHA-256 hash-chained to the previous entry (see `docs/observability/audit-trail.md`).

## Implementation References

- `main.py` — scenario runner, `run_single_scenario()`
- `agents/orchestrator.py` — `ComplianceOrchestrator.run_scenario()`, graph nodes
- `agents/transaction_monitor.py` — `TransactionMonitor.analyze_transaction_batch()`
- `agents/communication_scanner.py` — `CommunicationScanner.scan_communications()`
- `agents/regulatory_tracker.py` — `RegulatoryTracker.analyze_regulatory_updates()`
- `agents/report_generator.py` — `ReportGenerator.generate_detection_report()`
- `consensus/resolver.py` — `ConsensusEngine.compute_consensus()`
- `escalation/framework.py` — `EscalationFramework.create_escalation()`
- `observability/audit_trail.py` — `AuditTrail.append()`
- `observability/dashboard.py` — `ComplianceDashboard`
- `protocols/message_schema.py` — `MessageEnvelope`, `DetectionPayload`
