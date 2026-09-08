# System Topology — Multi-Agent Compliance Monitoring System

**Version:** 1.0.0
**Date:** September 2026
**Status:** Final

---

## 1. Overview

The MACS system uses a **hierarchical topology** — a central orchestrator coordinates four specialist agents organized in a tree structure. This balances coordination simplicity with fault tolerance, making it most suitable for compliance monitoring where guaranteed execution order and comprehensive audit trails are required.

### Why Hierarchical (Not Centralized or Decentralized)

- **Centralized** (single point of failure): Too risky for compliance monitoring where downtime means unmonitored violations
- **Decentralized** (peer-to-peer): Hard to guarantee execution order and audit trail completeness
- **Hierarchical** (tree with supervisor): The orchestrator ensures execution order while specialists handle domain logic independently

---

## 2. Topology Diagram

```
                          ┌─────────────────────┐
                          │   EXTERNAL SYSTEMS   │
                          │  (Trading Platform,  │
                          │   Email Servers,     │
                          │   Regulatory Feeds)  │
                          └──────────┬──────────┘
                                     │
                          ┌──────────▼──────────┐
                          │    ORCHESTRATOR      │
                          │     (ORCH-001)       │
                          │                      │
                          │  - Signal Intake     │
                          │  - Agent Dispatch    │
                          │  - Consensus         │
                          │  - Escalation        │
                          │  - Report Coord      │
                          └──┬───┬───┬───┬───┬──┘
                             │   │   │   │   │
              ┌──────────────┤   │   │   │   ├──────────────┐
              │              │   │   │   │   │              │
     ┌────────▼─────┐  ┌────▼───┴┐  │  ┌┴───┴────┐  ┌─────▼────────┐
     │ TRAN. MONITOR │  │  COMM   │  │  │ REG.   │  │   REPORT     │
     │   (TM-001)   │  │ SCANNER │  │  │ TRACKER│  │  GENERATOR   │
     │              │  │ (CS-001)│  │  │(RU-001)│  │   (RG-001)   │
     │ • Patterns   │  │ • NLP   │  │  │ • Feeds│  │ • Templates  │
     │ • Thresholds │  │ • Sent. │  │  │ • Impact│ │ • Audience   │
     │ • Temporal   │  │ • Barrier│ │  │ • Conflict││ • Filing     │
     │ • Counterp.  │  │ • Records│ │  │ • Precedent││ • Evidence   │
     │ • Cross-Mkt  │  │ • Priv. │  │  │         │  │              │
     └──────────────┘  └─────────┘  │  └─────────┘  └──────────────┘
                                    │
                          ┌─────────▼─────────┐
                          │  CONSENSUS ENGINE  │
                          │                    │
                          │ • Bayesian Update  │
                          │ • Dempster-Shafer  │
                          │ • Conflict Resolver│
                          └─────────┬─────────┘
                                    │
                          ┌─────────▼─────────┐
                          │ ESCALATION FRAMEWORK│
                          │                    │
                          │ Tier 1: Analyst    │
                          │ Tier 2: Senior     │
                          │ Tier 3: Manager    │
                          │ Tier 4: Director   │
                          └─────────┬─────────┘
                                    │
                          ┌─────────▼─────────┐
                          │   AUDIT TRAIL      │
                          │  (Hash-Chain)      │
                          └───────────────────┘
```

---

## 3. Component Relationships

### 3.1 Orchestrator → Agents (1:N)
The orchestrator dispatches work to agents and collects results. Communication is via the message protocol (ALERT, QUERY, RESPONSE, UPDATE types).

### 3.2 Agent → Consensus (N:1)
All agent assessments flow into the consensus engine for conflict resolution and final decision.

### 3.3 Consensus → Escalation (1:1)
If consensus determines a violation, the escalation framework manages human review.

### 3.4 All Components → Audit Trail (N:1)
Every action by every component is logged to the tamper-evident audit trail.

---

## 4. Communication Patterns

| Pattern | Where Used | Rationale |
|---------|-----------|-----------|
| Request-Response | Orchestrator → Agent queries | Synchronous, low-latency for real-time monitoring |
| Event-Driven | Agent → Orchestrator detections | Natural fit for compliance events triggering analysis |
| Publish-Subscribe | Regulatory updates broadcast | Multiple agents need the same regulatory change |
| Blackboard | Shared state in LangGraph | Agents read/write to shared compliance state |

---

## 5. Data Flow

### 5.1 Inbound (Source Systems → Agents)

```
Trading Platform ──→ Transaction Monitor (real-time stream)
Email/IM Servers ──→ Communication Scanner (batch + real-time)
Regulatory Feeds ──→ Regulatory Update Tracker (periodic polling)
```

### 5.2 Internal (Agent ↔ Agent via Orchestrator)

```
TM Detection ──→ Orchestrator ──→ Consensus ──→ Escalation
CS Detection ──→ Orchestrator ──→ Consensus ──→ Escalation
RU Detection ──→ Orchestrator ──→ Consensus ──→ Escalation
```

### 5.3 Outbound (System → Outputs)

```
Escalation ──→ Human Review Dashboard
Consensus  ──→ Report Generator ──→ Formatted Reports
All Events ──→ Audit Trail (hash-chained)
```

---

## 6. Scalability Considerations

| Dimension | Current Design | Scaling Strategy |
|-----------|---------------|-----------------|
| Transaction Volume | 2.4M/day | Horizontal agent scaling, batch partitioning |
| Communication Volume | 850K/day | NLP model parallelization, priority queuing |
| Regulatory Feeds | 23 bodies | Feed-specific worker agents |
| Concurrent Investigations | 100+ | Workflow state partitioning |

---

## 7. Failure Modes

| Component | Failure Mode | Mitigation |
|-----------|-------------|-----------|
| Transaction Monitor | Goes offline mid-trading-day | Heartbeat monitoring, auto-restart, degraded mode (reduce detection scope) |
| Communication Scanner | NLP model overload | Priority queuing, batch degradation, async processing |
| Regulatory Tracker | Feed source unavailable | Cached feed data, fallback to manual monitoring alerts |
| Report Generator | Template rendering failure | Graceful degradation to plain-text reports |
| Orchestrator | Single point of failure | Checkpoint-based recovery via LangGraph state persistence |
| Consensus Engine | Inconsistent results | Deterministic algorithm, fixed-point convergence check |
# Docs update
