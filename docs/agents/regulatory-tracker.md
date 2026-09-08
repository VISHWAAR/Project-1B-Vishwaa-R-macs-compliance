# Regulatory Update Tracker Agent (RU-001)

## Overview

The Regulatory Update Tracker continuously monitors the regulatory landscape across all operating jurisdictions. It detects new regulations, amendments, enforcement actions, guidance documents, no-action letters, and consultation papers. It assesses the impact of regulatory changes on existing policies, extracts implementation deadlines, identifies cross-jurisdiction conflicts, and analyzes enforcement precedents to calibrate detection thresholds.

**Agent ID:** RU-001  
**Module:** `agents/regulatory_tracker.py`  
**Class:** `RegulatoryTracker`

## Detection Pipeline

The agent runs 4 detection pipelines on each regulatory update batch:

```
analyze_regulatory_updates(updates, scenario_id, context)
│
├─ _detect_regulatory_change()         → REGULATORY_CHANGE
├─ _detect_cross_jurisdiction_conflict() → REGULATORY_CHANGE (conflict)
├─ _detect_enforcement_action_impact() → REGULATORY_CHANGE (enforcement)
└─ _detect_sanctions_update()          → SANCTIONS_VIOLATION
```

## Monitored Jurisdictions

The agent monitors regulatory bodies across 4 regions:

| Region | Regulatory Bodies |
|--------|-------------------|
| US | SEC, FINRA, OCC, CFPB |
| UK/EU | FCA, ECB/SSM |
| APAC | MAS, HKMA, JFSA, ASIC |
| India | SEBI, RBI |

Total: 12 regulatory bodies monitored.

## Detection Methods

### Regulatory Change Detection

Detects when a new regulation is published that requires system updates. Uses context flags:

```python
if context.get("regulatory_change_detected", False):
    # confidence = 0.5 + impact_score * 0.4, capped at 0.95
    # severity: MEDIUM
```

### Cross-Jurisdiction Conflict Detection

Detects when regulations from two different jurisdictions impose contradictory requirements:

```python
if context.get("jurisdictional_conflict", False):
    # confidence from context (default 0.75)
    # severity: HIGH
    # flags both jurisdictions for human legal review
```

### Enforcement Action Impact Detection

Detects enforcement actions against other institutions that may affect our compliance posture:

```python
if context.get("enforcement_action", False):
    # confidence from context (default 0.65)
    # severity: MEDIUM (medium applicability) or HIGH (high applicability)
```

### Sanctions Update Detection

Detects when an entity is added to the SDN (Specially Designated Nationals) list, making existing transactions potentially violative:

```python
if context.get("ru_signals") and context.get("sdn_match"):
    # confidence: 0.85
    # severity: CRITICAL
    # Requires SAR filing consideration
```

This is the key coordination point with TM-001: TM flags the wire transfer pattern, RU confirms the SDN match.

## Impact Assessment

The `assess_impact_on_system()` method evaluates how a regulatory change affects the existing compliance system:

```python
def assess_impact_on_system(self, detection, current_policies):
    # Returns: affected_agents, policy_gaps, recommended_actions,
    #          estimated_implementation_days, priority
```

For major US/EU regulatory changes, all 4 agents (TM-001, CS-001, RU-001, RG-001) are flagged as needing updates.

## Constraints

- Cannot provide legal interpretations of ambiguous regulatory language
- Impact assessments are preliminary and require human validation
- Cannot independently modify compliance rules
- Coverage limited to official regulatory sources (no social media, news, or informal channels)

## Resource Requirements

| Resource | Value |
|----------|-------|
| CPU Cores | 2.0 |
| Memory | 1024 MB |
| Max Concurrent Tasks | 10 |
| SLA Throughput | 50 events/sec |
| SLA Max Latency | 5000 ms |
| SLA Availability | 99.5% |

## Dependencies

- None (RU-001 is the most independent agent — it monitors external feeds)

## Scenario Coverage

| Scenario | RU Role |
|----------|---------|
| CS-07 (Regulatory Change) | Primary — detects new SEC margin rule, assesses 120-day implementation deadline |
| CS-09 (Sanctions) | Coordinating — confirms SDN match for wire transfer flagged by TM |
| CS-11 (Data Privacy) | Primary — detects cross-border data transfer conflict (EU vs non-adequate jurisdiction) |
| CS-19 (Multi-Jurisdiction Conflict) | Primary — detects contradictory regulations between jurisdictions |
| CS-20 (Coordinated AML) | Supporting — provides regulatory context for coordinated AML violation |

## Implementation

See `agents/regulatory_tracker.py` — `RegulatoryTracker` class, all `_detect_*` methods, `assess_impact_on_system()`, `MONITORED_JURISDICTIONS` list.
