# Escalation Decision Trees

## Overview

This document provides visual decision trees for the escalation framework. These trees map out the decision logic from detection event through tier assignment, SLA monitoring, and resolution.

## Tree 1: Escalation Trigger Decision Tree

```
                        ┌─────────────────────────┐
                        │  DETECTION EVENT         │
                        │  (any agent)             │
                        └───────────┬─────────────┘
                                    │
                                    ▼
                        ┌─────────────────────────┐
                        │  Confidence ≥ 0.8?       │
                        └───────┬────────┬────────┘
                                │ Yes    │ No
                                ▼        ▼
                        ┌─────────┐  ┌─────────────────┐
                        │ TRIGGER │  │ Confidence <    │
                        │ SET     │  │ 0.8 — check     │
                        │ HIGH_   │  │ other triggers  │
                        │ CONF    │  └────────┬────────┘
                        └────┬────┘           │
                             │                ▼
                             └─────────┬───┴───────────────┐
                                       │                   │
                                       ▼                   ▼
                              ┌──────────────┐   ┌──────────────────┐
                              │ Severity ==   │   │ Any agents       │
                              │ CRITICAL?     │   │ disagree?        │
                              └──────┬───────┘   │ (detect +        │
                                     │ Yes       │  non-detect)     │
                                     ▼           └──────┬───────────┘
                              ┌──────────┐            │ Yes
                              │ TRIGGER  │            ▼
                              │ SET      │   ┌──────────────┐
                              │ CRITICAL │   │ TRIGGER SET  │
                              └────┬─────┘   │ MULTI_AGENT  │
                                   │          └──────┬───────┘
                                   │ No             │
                                   ▼                │
                              ┌──────────┐         │
                              │ How many │         │
                              │ juris-   │         │
                              │ dictions?│         │
                              └───┬───┬──┘         │
                                  │   │            │
                                  │   │ ≥2         │
                                  │   ▼           │
                                  │ ┌───────────┐ │
                                  │ │ TRIGGER   │ │
                                  │ │ CROSS_    │ │
                                  │ │ JURISDICT │ │
                                  │ └─────┬─────┘ │
                                  │       │       │
                                  │       │       │
                                  ▼       ▼       ▼
                          ┌────────────────────────────────┐
                          │  DETERMINE INITIAL TIER         │
                          │                                 │
                          │  CRITICAL + CROSS_JURISDICT    │
                          │  → TIER 4 (Director/CCO)       │
                          │                                 │
                          │  CRITICAL only                  │
                          │  → TIER 3 (Manager)            │
                          │                                 │
                          │  HIGH or MULTI_AGENT_CONFLICT  │
                          │  → TIER 2 (Senior Analyst)     │
                          │                                 │
                          │  Default (low confidence,      │
                          │  single agent, no severity)    │
                          │  → TIER 1 (Analyst)            │
                          └────────────────┬───────────────┘
                                           │
                                           ▼
                          ┌────────────────────────────────┐
                          │  BUILD DECISION SUPPORT         │
                          │  PACKAGE (DSP)                  │
                          │                                 │
                          │  - Detection summary            │
                          │  - All agent assessments        │
                          │  - Consensus result             │
                          │  - Evidence summary             │
                          │  - Regulatory citations         │
                          │  - Recommended actions          │
                          │  - Risk assessment              │
                          └────────────────┬───────────────┘
                                           │
                                           ▼
                          ┌────────────────────────────────┐
                          │  CREATE ESCALATION RECORD       │
                          │  ESC-NNNNNN                     │
                          │  Status: ACTIVE                 │
                          │  Tier: T1/T2/T3/T4             │
                          │  SLA deadline: now + SLA_window │
                          └────────────────┬───────────────┘
                                           │
                                           ▼
                          ┌────────────────────────────────┐
                          │  AWAIT HUMAN REVIEW             │
                          │                                 │
                          │  ┌──────────────────────────┐  │
                          │  │ SLA breached?            │  │
                          │  │ (elapsed > SLA_seconds)? │  │
                          │  └──────────┬───────────────┘  │
                          │             │ Yes              │
                          │             ▼                │
                          │  ┌──────────────────────────┐ │
                          │  │ AUTO-ESCALATE to next    │ │
                          │  │ tier (if < Tier 4)       │ │
                          │  │ Log warning              │ │
                          │  └──────────┬───────────────┘ │
                          │             │ No               │
                          │             ▼                │
                          │  ┌──────────────────────────┐ │
                          │  │ Human decision received  │ │
                          │  │ - decision               │ │
                          │  │ - rationale              │ │
                          │  │ - decided_by             │ │
                          │  └──────────┬───────────────┘ │
                          │             │                │
                          │             ▼                │
                          │  ┌──────────────────────────┐ │
                          │  │ AUTHORIZATION CHECK      │ │
                          │  │ - file_sar → Tier 3+   │ │
                          │  │ - notify_regulator →   │ │
                          │  │   Tier 3+              │ │
                          │  │ - initiate_trade_halt →│ │
                          │  │   Tier 3+              │ │
                          │  │ - board_notification → │ │
                          │  │   Tier 4 only         │ │
                          │  └──────────┬───────────────┘ │
                          │             │                │
                          │             ▼                │
                          │  ┌──────────────────────────┐ │
                          │  │ RESOLVE: move to        │ │
                          │  │ _resolved_escalations   │ │
                          │  │ Log decision            │ │
                          │  └──────────────────────────┘ │
                          └────────────────────────────────┘
```

## Tree 2: Consensus-to-Escalation Decision Tree

```
                        ┌─────────────────────────┐
                        │  CONSENSUS RESULT        │
                        │  (from ConsensusEngine)  │
                        └───────────┬─────────────┘
                                    │
                                    ▼
                        ┌─────────────────────────┐
                        │  final_decision ==       │
                        │  "detect"?               │
                        └───────┬────────┬────────┘
                                │ Yes    │ No
                                ▼        ▼
                        ┌─────────┐  ┌─────────────────┐
                        │ Any     │  │ No detection    │
                        │ agents  │  │ → No escalation │
                        │ detect  │  │ (CS-18 path:    │
                        │ with    │  │  NO_ALERT)      │
                        │ conf ≥  │  └─────────────────┘
                        │ 0.7?    │
                        └────┬────┘
                             │ Yes
                             ▼
                        ┌─────────────────────────┐
                        │  Create escalation      │
                        │  (create_escalation())  │
                        └───────────┬─────────────┘
                                    │
                                    ▼
                        ┌─────────────────────────┐
                        │  Escalation created:    │
                        │  - ESC-NNNNNN           │
                        │  - Tier assigned        │
                        │  - DSP built            │
                        │  - Audit: escalation.   │
                        │    created logged       │
                        │  - Dashboard: recorded  │
                        └─────────────────────────┘
```

## Tree 3: Conflict-Driven Escalation

```
                        ┌─────────────────────────┐
                        │  MULTI-AGENT ASSESSMENTS│
                        │  (3 agents report)      │
                        └───────────┬─────────────┘
                                    │
                                    ▼
                        ┌─────────────────────────┐
                        │  Agents agree on         │
                        │  violation?              │
                        └───────┬────────┬────────┘
                                │ Yes    │ No
                                ▼        ▼
                        ┌─────────┐  ┌─────────────────┐
                        │ Same    │  │ DISAGREEMENT    │
                        │ severity│  │ → MULTI_AGENT   │
                        │ → No   │  │ CONFLICT trigger│
                        │ conflict│  │ → Escalate to   │
                        │         │  │ at least Tier 2 │
                        └────┬────┘  └────────┬────────┘
                             │               │
                             ▼               ▼
                        ┌────────────────────────────────┐
                        │  If ANY agent is RU-001 and   │
                        │  reports jurisdictional_       │
                        │  conflict → add CROSS_        │
                        │  JURISDICTIONAL trigger       │
                        │  → May push to Tier 4          │
                        └────────────────────────────────┘
```

## Node Decision Table

| Decision Node | Condition | Outcome |
|--------------|-----------|---------|
| Confidence ≥ 0.8? | `detection.confidence >= 0.8` | Set HIGH_CONFIDENCE_DETECTION trigger |
| Severity == CRITICAL? | `detection.severity == "CRITICAL"` | Set CRITICAL_SEVERITY trigger |
| Agents disagree? | detecting > 0 AND non-detecting > 0 | Set MULTI_AGENT_CONFLICT trigger |
| Jurisdictions ≥ 2? | `len(detection.jurisdictions) >= 2` | Set CROSS_JURISDICTIONAL trigger |
| SLA breached? | `elapsed > sla_seconds` | Auto-escalate to next tier |
| Decision authorized? | `tier >= required_min_tier` | Accept decision; otherwise warn |

## Implementation

See `escalation/framework.py`:
- `evaluate_triggers()` — nodes: confidence, severity, disagreement, jurisdiction
- `_determine_initial_tier()` — tier assignment logic
- `build_decision_support_package()` — DSP construction
- `check_auto_escalation()` — SLA breach check + auto-escalation
- `handle_decision()` — human decision + authorization check
