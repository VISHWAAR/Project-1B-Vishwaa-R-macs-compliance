# Escalation Framework

## Overview

The Escalation Framework implements a 4-tier Human-in-the-Loop (HITL) system for compliance monitoring. When the multi-agent system detects a potential violation, the framework determines whether human review is needed, assigns the appropriate tier based on severity and urgency, builds a decision support package for the human reviewer, and manages the lifecycle from creation through resolution (including auto-escalation when SLAs are missed).

## 4-Tier Architecture

```
                    ┌─────────────────────────┐
                    │   ESCALATION FRAMEWORK   │
                    └───────────┬─────────────┘
                                │
            ┌───────────────────┼───────────────────┐
            │                   │                   │
            ▼                   ▼                   ▼
    ┌───────────────┐  ┌───────────────┐  ┌───────────────┐
    │  TIER 1       │  │  TIER 2       │  │  TIER 3       │
    │  Analyst      │  │  Senior       │  │  Manager      │
    │               │  │  Analyst      │  │               │
    ├───────────────┤  ├───────────────┤  ├───────────────┤
    │ SLA: 15 min   │  │ SLA: 1 hour   │  │ SLA: 4 hours  │
    │               │  │               │  │               │
    │ Authorities:  │  │ Authorities:  │  │ Authorities:  │
    │ - acknowledge │  │ - all Tier 1  │  │ - all Tier 2  │
    │ - request     │  │ - initiate    │  │ - file_sar    │
    │   more data   │  │   investigation│  │ - notify      │
    │ - dismiss FP  │  │ - modify      │  │   regulator   │
    │               │  │   thresholds  │  │ - trade halt  │
    └───────────────┘  └───────────────┘  └───────────────┘
                                │
                                ▼
                    ┌───────────────┐
                    │  TIER 4       │
                    │  Director/CCO │
                    ├───────────────┤
                    │ SLA: 24 hours │
                    │               │
                    │ Authorities:  │
                    │ - all Tier 3  │
                    │ - board       │
                    │   notification│
                    │ - self-report │
                    │   to regulator│
                    └───────────────┘
```

## Tier Assignment Logic

The initial tier is determined by the escalation triggers that fired:

```python
# escalation/framework.py — _determine_initial_tier()

# CRITICAL severity + cross-jurisdictional → Tier 4
if severity == "CRITICAL":
    if EscalationTrigger.CROSS_JURISDICTIONAL in triggers:
        return EscalationTier.TIER_4_DIRECTOR
    return EscalationTier.TIER_3_MANAGER

# HIGH severity or multi-agent conflict → Tier 2
if severity == "HIGH" or EscalationTrigger.MULTI_AGENT_CONFLICT in triggers:
    return EscalationTier.TIER_2_SENIOR

# Default → Tier 1
return EscalationTier.TIER_1_ANALYST
```

### Trigger-Based Escalation Matrix

| Trigger Combination | Initial Tier |
|--------------------|--------------|
| CRITICAL severity only | Tier 3 (Manager) |
| CRITICAL + cross-jurisdictional | Tier 4 (Director/CCO) |
| HIGH severity | Tier 2 (Senior Analyst) |
| Multi-agent conflict | Tier 2 (Senior Analyst) |
| High confidence detection (≥ 0.8) | Tier 1 (Analyst) — unless other triggers elevate |
| Default (low confidence, single agent, no severity) | Tier 1 (Analyst) |

## Escalation Triggers

The framework evaluates 8 trigger types:

```python
class EscalationTrigger(Enum):
    HIGH_CONFIDENCE_DETECTION = "high_confidence_detection"   # confidence ≥ 0.8
    CRITICAL_SEVERITY = "critical_severity"                   # severity == CRITICAL
    MULTI_AGENT_CONFLICT = "multi_agent_conflict"             # detecting + non-detecting agents
    SLA_BREACH = "sla_breach"                                  # human review overdue
    RECURRING_VIOLATION = "recurring_violation"               # same violation ≥ 3 times
    REGULATORY_DEADLINE = "regulatory_deadline"               # implementation deadline approaching
    CROSS_JURISDICTIONAL = "cross_jurisdictional"             # ≥ 2 jurisdictions affected
    HUMAN_OVERRIDE_REQUEST = "human_override_request"         # agent requests human override
```

Trigger thresholds (configurable):

| Trigger | Threshold |
|---------|-----------|
| HIGH_CONFIDENCE_DETECTION | confidence ≥ 0.8 |
| CRITICAL_SEVERITY | severity == "CRITICAL" |
| MULTI_AGENT_CONFLICT | ≥ 2 conflicting agents |
| SLA_BREACH | overdue by ≥ 300 seconds |
| RECURRING_VIOLATION | ≥ 3 occurrences |
| CROSS_JURISDICTIONAL | ≥ 2 jurisdictions |
| REGULATORY_DEADLINE | deadline within window |
| HUMAN_OVERRIDE_REQUEST | agent requests it |

## Decision Support Package

Every escalation includes a comprehensive Decision Support Package (DSP) that gives the human reviewer everything they need to make an informed decision:

```python
@dataclass
class DecisionSupportPackage:
    detection_summary: Dict[str, Any]      # What was detected
    agent_assessments: Dict[str, Dict]    # Each agent's view
    consensus_result: Dict[str, Any]      # Consensus resolution
    evidence_summary: List[Dict]          # Key evidence from each agent
    regulatory_citations: List[str]       # Specific regulations implicated
    similar_cases: List[Dict]             # Historical similar cases (placeholder)
    recommended_actions: List[str]        # System-recommended next steps
    risk_assessment: Dict[str, Any]       # Financial, regulatory, reputational risk
```

### Example DSP for CS-01 (Insider Trading):

```
Detection Summary:
  - Violation: INSIDER_TRADING
  - Severity: CRITICAL
  - Confidence: 0.85
  - Description: Pre-announcement accumulation detected: 18 days before event, 35.0% price increase

Agent Assessments:
  - TM-001: detected=True, confidence=0.85, severity=CRITICAL
  - CS-001: detected=True, confidence=0.75, severity=HIGH

Consensus Result:
  - Final Decision: detect
  - Overall Confidence: 0.78
  - Bayesian Posterior: 0.81
  - D-S Belief: 0.75

Recommended Actions:
  1. Initiate immediate investigation
  2. Preserve all related communications and records
  3. Notify senior management within 24 hours

Risk Assessment:
  - Financial Risk: high
  - Regulatory Risk: high
  - Reputational Risk: high
```

## Escalation Lifecycle

```
┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐
│ CREATED  │ ──► │ ACTIVE   │ ──► │ RESOLVED │ ──► │ ARCHIVED │
└──────────┘     └──────────┘     └──────────┘     └──────────┘
     │                │                │
     │ create_        │ check_        │ handle_       │
     │ escalation()   │ auto_         │ decision()    │
     │                │ escalation()  │               │
     │                │                │
     │                │ ◄── SLA       │
     │                │     breach ──┘
     │                │
     │                │ If no human
     │                │ response in
     │                │ SLA window:
     │                │ auto-escalate
     │                │ to next tier
     ▼                ▼
```

### Lifecycle States

| State | Description |
|-------|-------------|
| **Created** | Escalation record created with ID, tier, triggers, DSP |
| **Active** | Waiting for human review within SLA window |
| **Resolved** | Human decision recorded with rationale |
| **Auto-escalated** | SLA breached, moved to next tier automatically |

### Creation

```python
# escalation/framework.py — EscalationFramework.create_escalation()

def create_escalation(
    self,
    detection_id: str,
    detection_data: Dict[str, Any],
    agent_assessments: Dict[str, Dict[str, Any]],
    consensus_result: Dict[str, Any],
) -> EscalationRecord:
    triggers = evaluate_triggers(detection_data, agent_assessments)
    tier = self._determine_initial_tier(triggers, detection_data)
    dsp = build_decision_support_package(detection_data, agent_assessments, consensus_result)
    record = EscalationRecord(
        escalation_id=f"ESC-{self._escalation_counter:06d}",
        detection_id=detection_id,
        current_tier=tier,
        triggered_by=triggers,
        decision_support=dsp,
    )
    self._active_escalations[escalation_id] = record
    return record
```

### Auto-Escalation

```python
# escalation/framework.py — EscalationFramework.check_auto_escalation()

def check_auto_escalation(self) -> List[EscalationRecord]:
    """Check for SLA breaches and auto-escalate."""
    for escalation_id, record in self._active_escalations.items():
        created = datetime.fromisoformat(record.created_at)
        elapsed = (now - created).total_seconds()
        sla = self._slas.get(record.current_tier, 86400)
        if elapsed > sla:
            if record.current_tier.value < EscalationTier.TIER_4_DIRECTOR.value:
                new_tier = EscalationTier(record.current_tier.value + 1)
                record.current_tier = new_tier
                record.auto_escalated = True
```

SLA deadlines:

| Tier | SLA |
|------|-----|
| Tier 1 (Analyst) | 15 minutes (900s) |
| Tier 2 (Senior Analyst) | 1 hour (3600s) |
| Tier 3 (Manager) | 4 hours (14400s) |
| Tier 4 (Director/CCO) | 24 hours (86400s) |

### Resolution

```python
# escalation/framework.py — EscalationFramework.handle_decision()

def handle_decision(
    self,
    escalation_id: str,
    decision: str,
    rationale: str,
    decided_by: str,
) -> Optional[EscalationRecord]:
    record = self._active_escalations.get(escalation_id)
    # Authorization check
    if decision in ("file_sar", "notify_regulator", "initiate_trade_halt"):
        if record.current_tier < EscalationTier.TIER_3_MANAGER:
            logger.warning(f"Decision '{decision}' requires Tier 3+")
    record.resolved_at = datetime.now(timezone.utc).isoformat()
    record.resolved_by = decided_by
    record.decision = decision
    record.rationale = rationale
    self._active_escalations.pop(escalation_id)
    self._resolved_escalations.append(record)
    return record
```

## EscalationRecord

```python
@dataclass
class EscalationRecord:
    escalation_id: str                          # ESC-000001
    detection_id: str                           # Scenario ID (e.g. CS-01)
    current_tier: EscalationTier                # TIER_1_ANALYST through TIER_4_DIRECTOR
    triggered_by: List[EscalationTrigger]      # Which triggers fired
    decision_support: DecisionSupportPackage    # Full review package
    created_at: str                             # ISO 8601 UTC
    resolved_at: Optional[str]                  # ISO 8601 UTC (if resolved)
    resolved_by: Optional[str]                  # Who resolved it
    decision: Optional[str]                     # approve, dismiss, escalate, etc.
    rationale: Optional[str]                    # Human's explanation
    auto_escalated: bool                        # Whether SLA auto-escalation occurred
```

## Statistics and Monitoring

```python
# escalation/framework.py — EscalationFramework.get_escalation_stats()

{
    "active_escalations": 5,
    "resolved_escalations": 42,
    "active_by_tier": {
        "tier_1": 2,
        "tier_2": 2,
        "tier_3": 1,
        "tier_4": 0,
    },
    "resolution_decisions": {
        "approve": 38,
        "dismiss": 4,
    },
}
```

## Scenario Coverage

| Scenario | Triggers | Initial Tier | Notes |
|----------|----------|--------------|-------|
| CS-01 (Insider Trading) | HIGH_CONFIDENCE, CRITICAL_SEVERITY | Tier 3 (Manager) | 18-day accumulation, 35% price jump, communication link |
| CS-02 (Spoofing) | HIGH_CONFIDENCE | Tier 1 or 2 | 92% cancel rate, 47 cancelled orders |
| CS-05 (Chinese Wall) | CRITICAL_SEVERITY, HIGH_CONFIDENCE | Tier 3 (Manager) | Cross-department breach |
| CS-09 (Sanctions) | CRITICAL_SEVERITY, HIGH_CONFIDENCE, CROSS_JURISDICTIONAL | Tier 4 (Director) | SDN match, multi-jurisdiction |
| CS-18 (False Positive) | None | No escalation | Correctly cleared — NO_ALERT |
| CS-20 (Coordinated AML) | All applicable triggers | Tier 4 (Director) | All 4 agents, CRITICAL, multi-jurisdiction, coordinated |

## Integration Points

| Component | Interaction |
|-----------|-------------|
| Orchestrator | Calls `create_escalation()` after consensus; stores escalation summary in state |
| Report Generator | Includes escalation summary in reports for management/board/regulator audiences |
| Audit Trail | Logs `escalation.created` event with full escalation payload |
| Dashboard | Records escalation in operational intelligence panel (by tier, by type) |
| Message Router | Escalation messages use Priority.CRITICAL for Tier 3+, Priority.HIGH for Tier 1-2 |

## Implementation

See `escalation/framework.py`:
- `EscalationFramework` — core framework class
- `EscalationRecord` — escalation data
- `DecisionSupportPackage` — human review package
- `EscalationTrigger` enum — 8 trigger types
- `EscalationTier` enum — 4 tiers
- `evaluate_triggers()` — trigger evaluation
- `build_decision_support_package()` — DSP construction
- `get_escalation_stats()` — statistics

See `escalation/escalation_tiers.py` (if exists — tier constants and SLA table).

See `docs/escalation/decision-trees/` for visual decision trees (if created).
