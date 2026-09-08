# Agent Registry Documentation

## Overview

The Agent Registry is the central catalog of all agents in the Multi-Agent Compliance Monitoring System (MACS). It maintains authoritative definitions for each agent's capabilities, resource requirements, and service level agreements (SLAs). The orchestrator consults this registry when routing messages and assigning tasks.

## Architecture

```
┌─────────────────────────────────────────────────────┐
│                  Agent Registry                      │
│  ┌───────────────────────────────────────────────┐  │
│  │  AgentDefinition (dataclass)                   │  │
│  │  ┌─────────────────────────────────────────┐  │  │
│  │  │ AgentCapability × N                     │  │  │
│  │  │ AgentResourceRequirements               │  │  │
│  │  │ AgentSLA                                │  │  │
│  │  └─────────────────────────────────────────┘  │  │
│  └───────────────────────────────────────────────┘  │
│                    ▲          ▲                      │
│                    │ register │                      │
│              TM-001        ORCH-001                  │
└─────────────────────────────────────────────────────┘
```

## Agent Definitions

### ORCH-001: Orchestrator

| Attribute | Value |
|-----------|-------|
| Agent ID | ORCH-001 |
| Role | Central coordinator |
| CPU Cores | 2.0 |
| Memory | 1024 MB |
| Max Concurrent Tasks | 50 |
| SLA Throughput | — (orchestrator, not throughput-bound) |
| SLA Max Latency | — |
| SLA Availability | — |

**Capabilities:**
- `workflow_orchestration` — Manage multi-agent compliance workflows
- `message_routing` — Route messages between agents
- `conflict_resolution` — Resolve inter-agent conflicts
- `escalation_management` — Manage human-in-the-loop escalation

**Dependencies:** None (central coordinator)

---

### TM-001: Transaction Monitor

| Attribute | Value |
|-----------|-------|
| Agent ID | TM-001 |
| Role | Trading/transaction surveillance |
| CPU Cores | 4.0 |
| Memory | 2048 MB |
| Max Concurrent Tasks | 20 |
| SLA Throughput | 1000 events/sec |
| SLA Max Latency | 500 ms |
| SLA Availability | 99.95% |

**Capabilities:**
- `pattern_detection` — Identify statistical anomalies in transaction data
- `threshold_monitoring` — Monitor regulatory thresholds (position limits, SAR triggers)
- `temporal_analysis` — Detect patterns across multiple time windows
- `counterparty_analysis` — Identify unusual counterparty concentrations
- `cross_market_surveillance` — Detect correlated patterns across multiple markets

**Constraints:**
- Cannot access raw customer communications (must rely on CS agent)
- Detection confidence scores must be calibrated against historical false positive rates
- Cannot issue trading halts autonomously
- Must maintain sub-second latency for real-time monitoring

**Dependencies:** CS-001

**Violation Types Detected:**
- Insider Trading (INSIDER_TRADING)
- Spoofing/Layering (SPOOFING_LAYERING)
- Wash Trading (WASH_TRADING)
- Front-Running (FRONT_RUNNING)
- AML Structuring (AML_STRUCTURING)
- Sanctions Violation (SANCTIONS_VIOLATION)
- Concentration Risk (CONCENTRATION_RISK)
- Late Trading (LATE_TRADING)
- Best Execution Failure (BEST_EXECUTION_FAILURE)

---

### CS-001: Communication Scanner

| Attribute | Value |
|-----------|-------|
| Agent ID | CS-001 |
| Role | Business communication surveillance |
| CPU Cores | 4.0 |
| Memory | 2048 MB |
| Max Concurrent Tasks | 20 |
| SLA Throughput | 500 events/sec |
| SLA Max Latency | 2000 ms |
| SLA Availability | 99.9% |

**Capabilities:**
- `keyword_detection` — Identify compliance-relevant keywords and code words
- `sentiment_intent_analysis` — Detect coercive language, misleading statements
- `information_barrier_monitoring` — Detect Chinese wall breaches
- `record_keeping_compliance` — Verify regulated communications are captured
- `privilege_detection` — Identify potentially privileged communications

**Constraints:**
- Cannot decrypt end-to-end encrypted communications
- Voice analysis limited to transcribed text
- Must respect data retention boundaries
- Cannot independently determine legal privilege
- Privacy-preserving analysis for personal communications

**Dependencies:** RU-001

**Violation Types Detected:**
- Misleading Statements (MISLEADING_STATEMENTS)
- Chinese Wall Breach (CHINESE_WALL_BREACH)
- Off-Channel Communications (OFF_CHANNEL_COMMS)
- Elder Exploitation (ELDER_EXPLOITATION)
- Record Keeping Failure (RECORD_KEEPING_FAILURE)
- Research Independence (RESEARCH_INDEPENDENCE)

---

### RU-001: Regulatory Update Tracker

| Attribute | Value |
|-----------|-------|
| Agent ID | RU-001 |
| Role | Regulatory landscape monitoring |
| CPU Cores | 2.0 |
| Memory | 1024 MB |
| Max Concurrent Tasks | 10 |
| SLA Throughput | 50 events/sec |
| SLA Max Latency | 5000 ms |
| SLA Availability | 99.5% |

**Capabilities:**
- `regulatory_feed_monitoring` — Monitor regulatory body publications
- `impact_assessment` — Assess impact of regulatory changes on existing policies
- `timeline_extraction` — Extract implementation deadlines from regulations
- `cross_regulation_conflict` — Identify conflicts between jurisdictions
- `precedent_analysis` — Analyze enforcement actions to calibrate thresholds

**Constraints:**
- Cannot provide legal interpretations of ambiguous regulatory language
- Impact assessments are preliminary and require human validation
- Cannot independently modify compliance rules
- Coverage limited to official sources

**Dependencies:** None

**Violation Types Detected:**
- Regulatory Change (REGULATORY_CHANGE)
- Sanctions Violation (SANCTIONS_VIOLATION — via SDN list monitoring)
- Data Privacy Violation (DATA_PRIVACY_VIOLATION)
- Cross-Jurisdictional Conflict (REGULATORY_CHANGE — conflict type)

---

### RG-001: Report Generator

| Attribute | Value |
|-----------|-------|
| Agent ID | RG-001 |
| Role | Compliance report compilation and distribution |
| CPU Cores | 2.0 |
| Memory | 1024 MB |
| Max Concurrent Tasks | 10 |
| SLA Throughput | 10 reports/sec |
| SLA Max Latency | 10000 ms |
| SLA Availability | 99.5% |

**Capabilities:**
- `scheduled_reports` — Automated daily/weekly/monthly/quarterly/annual reports
- `event_triggered_reporting` — Immediate report for critical events (SAR/STR)
- `multi_audience_adaptation` — Adjust detail and format per target audience
- `evidence_compilation` — Compile supporting evidence with source attribution
- `regulatory_filing_preparation` — Generate filing drafts (XBRL, XML, PDF)

**Constraints:**
- Cannot file regulatory reports without human authorisation (dual sign-off required)
- Report templates must be version-controlled
- Cannot include privileged materials without legal clearance
- Distribution lists are controlled

**Dependencies:** TM-001, CS-001, RU-001

## Capability Matrix

| Agent | Capabilities |
|-------|-------------|
| ORCH-001 | workflow_orchestration, message_routing, conflict_resolution, escalation_management |
| TM-001 | pattern_detection, threshold_monitoring, temporal_analysis, counterparty_analysis, cross_market_surveillance |
| CS-001 | keyword_detection, sentiment_intent_analysis, information_barrier_monitoring, record_keeping_compliance, privilege_detection |
| RU-001 | regulatory_feed_monitoring, impact_assessment, timeline_extraction, cross_regulation_conflict, precedent_analysis |
| RG-001 | scheduled_reports, event_triggered_reporting, multi_audience_adaptation, evidence_compilation, regulatory_filing_preparation |

## Data Flow Between Agents

```
                    ┌──────────┐
                    │ RU-001   │ (Regulatory updates)
                    └────┬─────┘
                         │
    ┌────────┬──────────┼──────────┬──────────┐
    │        │          │           │          │
┌───┴───┐ ┌──┴───┐ ┌───┴───┐ ┌────┴─────┐ ┌──┴───┐
│ TM-001│ │CS-001│ │ RU-001│ │  RG-001  │ │ORCH-001│
│(TM)   │ │(CS)  │ │(RU)   │ │(Reports) │ │(Coord)│
└───┬───┘ └──┬───┘ └───┬───┘ └────┬─────┘ └──┬───┘
    │        │          │           │          │
    └────────┴──────────┴───────────┴──────────┘
                         │
                    ┌────┴─────┐
                    │ ORCH-001 │ (Final decision, escalation, audit)
                    └──────────┘
```

## Agent Pair Interactions

| Agent Pair | Shared Data Types | Direction |
|------------|-------------------|-----------|
| TM-001 → CS-001 | transaction patterns requiring communication context | Unidirectional |
| CS-001 → TM-001 | communication-based evidence for TM alerts | Unidirectional |
| RU-001 → TM-001 | sanctions list updates, regulatory thresholds | Unidirectional |
| RU-001 → CS-001 | regulatory changes affecting comms requirements | Unidirectional |
| All → ORCH-001 | detection events, confidence scores, evidence | Unidirectional |
| ORCH-001 → RG-001 | consensus results, escalation records | Unidirectional |

## Registration Lifecycle

1. **Startup:** `AgentRegistry.__init__()` creates instance and calls `_register_default_agents()`
2. **Registration:** Each agent calls `register(AgentDefinition(...))` during startup
3. **Query:** Orchestrator calls `get(agent_id)` and `get_capabilities_matrix()` during message routing
4. **Runtime:** No dynamic registration — agents are statically defined for production stability

## Error Handling

- **Unknown agent lookup:** `get(agent_id)` returns `None` — orchestrator skips routing
- **Malformed definition:** Registration validates SLA/constraints at construction time
- **Dependency not registered:** Warnings logged; agent proceeds with reduced capability set

## Implementation

See: `agents/registry.py` — `AgentRegistry` class, `AgentDefinition` dataclass, `get_agent_registry()` singleton.
