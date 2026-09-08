# Failure Modes and Resilience

## Overview

This document catalogs the known failure modes of the MACS system, their severity, detection mechanisms, and mitigation strategies. The system is designed for high availability in a regulated environment where missed detections are more costly than false positives.

## Agent-Level Failure Modes

### TM-001: Transaction Monitor

| Failure Mode | Symptom | Detection | Mitigation |
|-------------|---------|-----------|------------|
| Pattern detection misses | False negative — no alert for actual insider trading | Scenario testing (CS-01 must trigger) | Threshold calibration against historical enforcement data; RU precedent analysis for threshold tuning |
| Latency spike | Batch analysis exceeds 500ms SLA | `performance_metric` monitoring, dashboard P95/P99 | Horizontal scaling — TM is stateless per-batch; add instances behind load balancer |
| False positive cascade | Too many alerts for legitimate activity | FP rate monitoring in dashboard (target < 5%) | CS-18 false positive check path; adjust confidence thresholds; human feedback loop via escalation dismissals |
| Data feed interruption | Zero transactions processed | Heartbeat monitoring, queue depth monitoring in router | Alert on queue depth > 0 for > SLA window; fallback to cached rules |
| Sanctions match incomplete | TM flags transaction but can't confirm SDN match | TM confidence at 0.70 (partial) by design | Requires RU coordination — RU confirms SDN list match; together they reach full confidence |

### CS-001: Communication Scanner

| Failure Mode | Symptom | Detection | Mitigation |
|-------------|---------|-----------|------------|
| Keyword blindness | New evasion tactics use synonyms not in lexicon | Scenario testing; human review of dismissed alerts | Lexicon updates via RU regulatory tracking; human feedback on dismissed alerts feeds lexicon expansion |
| Encrypted channel blind spot | E2E-encrypted comms not scanned | Architectural constraint (documented, not a failure per se) | Voice transcription pipeline; endpoint monitoring for unencrypted channels |
| Language coverage gap | Non-English comms missed | Scenario testing with multi-language comms | Multi-language lexicon maintenance; additional language packs |
| Privilege misclassification | Legitimate privileged comms flagged | Human review of flagged privileged comms | Privilege detection is advisory only — human makes final privilege determination |
| Volume overload | 3400+ emails in CS-08 scenario | Processing latency > 2000ms SLA | Batch processing with backpressure; queue depth monitoring |

### RU-001: Regulatory Tracker

| Failure Mode | Symptom | Detection | Mitigation |
|-------------|---------|-----------|------------|
| Feed gap | Regulatory publication missed | No RU detections despite active feed monitoring | Feed health monitoring; multiple feed sources per regulator; alert on feed staleness > 24h |
| Impact assessment error | System updates thresholds incorrectly | Human validation of all RU impact assessments (architectural constraint) | RU assessments are preliminary; human reviews before system changes |
| Jurisdiction gap | New jurisdiction not monitored | Cross-jurisdictional conflict not detected | Jurisdiction expansion tracked via regulatory change events; periodic coverage audit |

### RG-001: Report Generator

| Failure Mode | Symptom | Detection | Mitigation |
|-------------|---------|-----------|------------|
| Report format error | Output doesn't match audience expectations | Report validation on generation | Audience profile validation; template version control |
| Missing dual sign-off | Report filed without human authorization | Architecural constraint — RG cannot file without human sign-off | RG always produces DRAFT status; filing requires Compliance Officer + MLRO sign-off |
| Evidence omission | Key evidence not included in report | Comprehensive report audience includes full evidence package | `auditor` and `regulator` profiles include `_build_evidence_package()` |

### ORCH-001: Orchestrator

| Failure Mode | Symptom | Detection | Mitigation |
|-------------|---------|-----------|------------|
| Graph compilation failure | Scenario doesn't start | Exception caught in `run_scenario()` | LangGraph graph validation at startup; health check endpoint |
| Agent timeout | One agent doesn't respond | No detection from that agent; error_log entry | Timeout handling — pipeline continues with other agents; no single point of failure |
| State corruption | Consensus produces nonsensical result | Inconsistent confidence vs. decision | Bounded confidence values (0.0-1.0); consensus decision logic sanity checks |
| Audit trail break | Hash chain broken | `verify_integrity()` detects break | Immutability — entries are append-only; any break is immediately detectable and reportable |

## Consensus Failure Modes

### Bayesian Consensus

| Failure Mode | Symptom | Mitigation |
|-------------|---------|------------|
| Prior sensitivity | Prior of 0.3 overly influences result when few agents report | Sensitivity analysis with different priors; documented in consensus spec |
| Independence assumption violated | Agents' detections are correlated (e.g., TM and CS both see same event) | D-S combination is more robust to correlated evidence; system uses both and weights them |

### Dempster-Shafer Consensus

| Failure Mode | Symptom | Mitigation |
|-------------|---------|------------|
| Total conflict (K → 1) | All evidence contradicts; normalization breaks | Handled: equal distribution across focal elements when K ≈ 1 |
| Empty focal elements | No mass assigned to any hypothesis | Handled: uniform distribution across frame |

### Conflict Taxonomy

| Conflict Type | Trigger | Resolution |
|--------------|---------|-----------|
| Type A: Severity disagreement | Agents agree violation occurred but disagree on severity | Highest severity among detecting agents wins (conservative — better to over-warn) |
| Type B: Detection disagreement | Some agents detect, others don't | Bayesian posterior governs; if posterior > 0.5, "detect" |
| Type C: Jurisdictional conflict | RU detects conflicting regulations from two jurisdictions | RU jurisdiction recommendation prevails; escalated for human legal review |

## Escalation Failure Modes

| Failure Mode | Symptom | Mitigation |
|-------------|---------|------------|
| SLA breach | Human reviewer doesn't respond in time | Auto-escalation to next tier (`check_auto_escalation()`) |
| Dead letter queue overflow | Message delivery fails repeatedly | DLQ max size 1000; oldest dropped when full; alert on DLQ size |
| Wrong tier assignment | Escalation starts too low (missed urgency) or too high (wasted senior time) | Trigger evaluation covers multiple dimensions (confidence, severity, conflict, jurisdiction); tier assignment logic reviewed per scenario |
| Unauthorized decision | Junior staff tries to file SAR | Authorization check in `handle_decision()`; warning logged; in production, hard reject |

## System-Level Failure Modes

### Single Point of Failure: Orchestrator

The orchestrator is currently a singleton. If it goes down, no scenarios process.

**Mitigation (future):** Stateless orchestrator design — state is in the graph state dict, not in orchestrator memory. Multiple orchestrator instances behind a queue-based work distribution. Currently: health check via heartbeat, alert on orchestrator stop.

### Memory Growth

Audit trail and detection history accumulate in memory unbounded.

**Mitigation (future):** Ring buffer with configurable retention window; export to persistent storage periodically. Current: suitable for scenario testing (20 scenarios × brief runtime). Not suitable for 24/7 operation without persistence layer.

### Logger Saturation

In-memory log entries grow without bound.

**Mitigation (future):** Periodic flush to persistent structured log sink; configurable retention per category. Current: suitable for scenario testing.

---

## Testing Coverage

Each failure mode is validated by at least one scenario:

| Scenario | Validates |
|----------|-----------|
| CS-01 | TM insider trading detection works (not a false negative) |
| CS-18 | False positive handling — legitimate block trade correctly returns NO_ALERT |
| CS-05 | CS Chinese wall detection works |
| CS-07 | RU regulatory change detection works |
| CS-09 | TM + RU coordination for sanctions (TM partial + RU confirmation) |
| CS-20 | All four agents invoked; coordinated violation detection; Tier 4 escalation |
| All scenarios | Consensus engine produces valid decision; escalation framework creates records; reports generated for all 5 audiences; audit trail entries created and chain verifiable |

---

## Implementation References

- `agents/transaction_monitor.py` — all `_detect_*` methods, `check_false_positive()`
- `agents/communication_scanner.py` — all `_detect_*` methods, lexicon constants
- `agents/regulatory_tracker.py` — `analyze_regulatory_updates()`, `_detect_*` methods
- `agents/report_generator.py` — `generate_detection_report()`, audience profiles
- `agents/orchestrator.py` — graph nodes, error handling, CS-18 false positive path
- `consensus/resolver.py` — `ConsensusEngine`, conflict taxonomy via `ConflictResolver`
- `consensus/bayesian.py` — Bayesian consensus
- `consensus/dempster_shafer.py` — D-S combination, conflict handling
- `escalation/framework.py` — `EscalationFramework`, auto-escalation, authorization checks
- `observability/audit_trail.py` — hash chain integrity verification
- `observability/dashboard.py` — failure metric panels
