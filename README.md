# MACS: Multi-Agent Compliance Monitoring System

**Agentic AI — Multi-Agent Compliance Monitoring System**

A production-grade multi-agent AI system where four specialized agents collaborate to monitor regulatory compliance across trading operations, lending activities, and customer communications at a tier-2 global bank (Meridian Global Bank).

## System Overview

The system addresses the core compliance challenge: monitoring 2.4 million daily transactions and 850,000 daily communications for regulatory violations across 23 distinct regulatory bodies — without simply hiring thousands more compliance officers.

### Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│                     ORCHESTRATOR (ORCH-001)                      │
│              LangGraph StateGraph — Central Coordinator           │
├──────────┬──────────┬──────────┬──────────┬─────────────────────┤
│    TM    │    CS    │    RU    │    RG    │   CONSENSUS ENGINE  │
│  Monitor │ Scanner  │ Tracker  │ Reporter │  Bayesian + D-S     │
│  (TM-001)│ (CS-001) │ (RU-001) │ (RG-001)│  Conflict Resolver   │
└────┬─────┴────┬─────┴────┬─────┴────┬─────┴──────────┬──────────┘
     │          │          │          │                │
     ▼          ▼          ▼          ▼                ▼
  Messages   Messages   Messages   Messages      ESCALATION
  ←→ Audit   ←→ Audit   ←→ Audit   ←→ Audit     FRAMEWORK
     Trail       Trail       Trail       Trail    4-Tier HITL
```

### Four Specialist Agents

| Agent | ID | Role | Key Capabilities |
|-------|-----|------|-----------------|
| **Transaction Monitor** | TM-001 | Surveillance of trading activity | Pattern detection, threshold monitoring, temporal analysis, cross-market surveillance |
| **Communication Scanner** | CS-001 | Monitor business communications | Keyword/sentiment detection, Chinese wall monitoring, off-channel detection, multi-language NLP |
| **Regulatory Update Tracker** | RU-001 | Monitor regulatory landscape | Feed monitoring, impact assessment, timeline extraction, cross-regulation conflict detection |
| **Report Generator** | RG-001 | Compile and distribute reports | Scheduled/event-triggered reports, multi-audience adaptation, evidence compilation, regulatory filing preparation |

### Consensus Engine

- **Bayesian Consensus**: Continuous belief updating via Bayes' theorem
- **Dempster-Shafer Theory**: Evidence combination with quantified uncertainty
- **Conflict Taxonomy**: 4 types of inter-agent disagreements with resolution strategies
- **Weighted Voting**: Domain-authority-weighted voting for final decisions

### Escalation Framework

| Tier | Role | SLA | Authority |
|------|------|-----|-----------|
| Tier 1 | Analyst | 15 minutes | Acknowledge, dismiss FP, request data |
| Tier 2 | Senior Analyst | 1 hour | + Initiate investigation, modify thresholds |
| Tier 3 | Manager | 4 hours | + File SAR, notify regulator, trade halt |
| Tier 4 | Director/CCO | 24 hours | + Board notification, self-report |

## Setup

```bash
# Clone the repo
cd Project-1B

# Create virtual environment
python -m venv .venv
source .venv/bin/activate   # or .venv\Scripts\activate on Windows

# Install dependencies
pip install -r requirements.txt

# Set up your API keys (optional — system works without LLM calls)
cp .env.example .env
```

## Running

```bash
# Run all 20 compliance scenarios
python main.py

# Run specific scenarios
python main.py 1 5 18

# Print evaluation dashboard
python main.py --summary
```

## Project Structure

```
├── agents/              Core agent implementations + orchestrator
│   ├── orchestrator.py  LangGraph StateGraph central coordinator
│   ├── transaction_monitor.py   TM agent — pattern detection
│   ├── communication_scanner.py CS agent — NLP, sentiment
│   ├── regulatory_tracker.py    RU agent — regulatory monitoring
│   ├── report_generator.py      RG agent — multi-audience reports
│   └── registry.py      Agent capability registry
├── protocols/           Inter-agent communication protocol
│   ├── message_schema.py    Pydantic models for all message types
│   ├── message_schema.json  JSON Schema export
│   └── routing.py           Message routing with SLA enforcement
├── consensus/           Conflict resolution algorithms
│   ├── bayesian.py      Bayesian consensus (Belief updating)
│   ├── dempster_shafer.py  Dempster-Shafer evidence combination
│   ├── conflict_taxonomy.py  4-type conflict classification
│   └── resolver.py      Top-level consensus orchestrator
├── escalation/          Human-in-the-loop framework
│   └── framework.py     4-tier escalation with SLA monitoring
├── observability/       Audit-grade monitoring
│   ├── logger.py        8-category structured logging
│   ├── audit_trail.py   SHA-256 hash chain tamper-evident logging
│   └── dashboard.py     3-panel monitoring dashboard
├── data/                Test data and generators
│   └── generators.py    20 scenario data generators
├── docs/                Architecture specification documents
│   ├── architecture/    System topology, agent registry, data flow
│   ├── protocols/       Communication protocol specs
│   ├── conflict-resolution/  Consensus algorithm specs
│   ├── escalation/      Escalation framework specs
│   ├── agents/          Individual agent specifications
│   └── observability/   Logging, audit, dashboard specs
├── tests/scenarios/     20 scenario trace-throughs (CS-01 to CS-20)
├── main.py              CLI scenario runner
├── SELF-ASSESSMENT.md   Self-assessment checklist
└── requirements.txt     Python dependencies
```

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Agent Framework | LangGraph (Plan-and-Execute + StateGraph) |
| LLM | OpenAI / Anthropic / Groq (auto-detected from .env) |
| Message Schema | Pydantic v2 + JSON Schema |
| Consensus | Custom Bayesian + Dempster-Shafer |
| Observability | Structured logging + SHA-256 hash chaining |
| Testing | pytest |
| Documentation | Markdown (GitHub-rendered) |

## Scenario Coverage

All 20 compliance scenarios from the specification are implemented:

| # | Scenario | Agents | Expected Alert |
|---|----------|--------|----------------|
| CS-01 | Insider Trading | TM + CS | CRITICAL |
| CS-02 | Spoofing | TM | HIGH |
| CS-03 | Unsuitable Recommendation | CS + TM | HIGH |
| CS-04 | AML Structuring | TM | CRITICAL |
| CS-05 | Chinese Wall Breach | CS | CRITICAL |
| CS-06 | Wash Trading | TM | HIGH |
| CS-07 | Regulatory Change | RU | MEDIUM |
| CS-08 | Misleading Marketing | CS | CRITICAL |
| CS-09 | Sanctions Violation | TM + RU | CRITICAL |
| CS-10 | Front-Running | TM | CRITICAL |
| CS-11 | Data Privacy | CS + RU | HIGH |
| CS-12 | Concentration Risk | TM | MEDIUM |
| CS-13 | Off-Channel Comms | CS | HIGH |
| CS-14 | Late Trading | TM | CRITICAL |
| CS-15 | Best Execution | TM | HIGH |
| CS-16 | Research Independence | CS + TM | CRITICAL |
| CS-17 | Elder Exploitation | TM + CS | CRITICAL |
| CS-18 | FALSE POSITIVE | TM | NO ALERT |
| CS-19 | Multi-Jurisdiction Conflict | RU | HIGH |
| CS-20 | Coordinated AML | ALL FOUR | CRITICAL |

## Document Errors Identified

Seven deliberate errors were identified in the assessment document (see ERROR_LOG.md):

1. **Error #1**: Memory Utilization Metric Formula (multiplication → division)
2. **Error #2**: Source Reliability Hierarchy Inversion (social media/news outlets swapped)
3. **Error #3**: SCAP/Dodd-Frank Historical Inaccuracy (2007→2009, timeline reversed)
4. **Error #4**: Full Stack Badge Tool Count (12→10 tools)
5. **Error #5**: Industry Hallucination Rate Understated (45-60% → 60-80%)
6. **Error #6**: Unrealistic Hallucination Rate Target (0 → <2%)
7. **Error #7**: OpenAI Free Tier Rate Limits Incorrect (500 RPM → 2-5 RPM)

## License

This is an educational project for the Zetheta Algorithms internship program.
