# Agent Capability Matrix

**Version:** 1.0.0

---

## 1. Capability Matrix

| Capability | TM-001 | CS-001 | RU-001 | RG-001 | ORCH-001 |
|-----------|--------|--------|--------|--------|----------|
| Transaction Pattern Detection | ✅ PRIMARY | ❌ | ❌ | ❌ | — |
| Threshold Monitoring | ✅ PRIMARY | ❌ | ❌ | ❌ | — |
| Temporal Analysis | ✅ PRIMARY | ❌ | ❌ | ❌ | — |
| Counterparty Analysis | ✅ PRIMARY | ❌ | ❌ | ❌ | — |
| Cross-Market Surveillance | ✅ PRIMARY | ❌ | ❌ | ❌ | — |
| Keyword Detection | ❌ | ✅ PRIMARY | ❌ | ❌ | — |
| Sentiment & Intent Analysis | ❌ | ✅ PRIMARY | ❌ | ❌ | — |
| Information Barrier Monitoring | ❌ | ✅ PRIMARY | ❌ | ❌ | — |
| Record-Keeping Compliance | ❌ | ✅ PRIMARY | ❌ | ❌ | — |
| Privilege Detection | ❌ | ✅ PRIMARY | ❌ | ❌ | — |
| Regulatory Feed Monitoring | ❌ | ❌ | ✅ PRIMARY | ❌ | — |
| Impact Assessment | ❌ | ❌ | ✅ PRIMARY | ❌ | — |
| Timeline Extraction | ❌ | ❌ | ✅ PRIMARY | ❌ | — |
| Cross-Regulation Conflict | ❌ | ❌ | ✅ PRIMARY | ❌ | — |
| Precedent Analysis | ❌ | ❌ | ✅ PRIMARY | ❌ | — |
| Scheduled Reports | ❌ | ❌ | ❌ | ✅ PRIMARY | — |
| Event-Triggered Reporting | ❌ | ❌ | ❌ | ✅ PRIMARY | — |
| Multi-Audience Adaptation | ❌ | ❌ | ❌ | ✅ PRIMARY | — |
| Evidence Compilation | ❌ | ❌ | ❌ | ✅ PRIMARY | — |
| Regulatory Filing Preparation | ❌ | ❌ | ❌ | ✅ PRIMARY | — |
| Workflow Orchestration | ❌ | ❌ | ❌ | ❌ | ✅ PRIMARY |
| Message Routing | ❌ | ❌ | ❌ | ❌ | ✅ PRIMARY |
| Consensus Resolution | ❌ | ❌ | ❌ | ❌ | ✅ PRIMARY |
| Escalation Management | ❌ | ❌ | ❌ | ❌ | ✅ PRIMARY |

## 2. Agent Boundaries

### TM-001 Boundaries
- **Can access**: Transaction data, order books, position data, counterparty databases
- **Cannot access**: Raw customer communications (must request from CS-001)
- **Cannot do**: Issue trading halts autonomously, access encrypted communications
- **SLA**: 1000 transactions/second, <500ms latency, 99.95% availability

### CS-001 Boundaries
- **Can access**: Email transcripts, IM logs, voice transcripts, social media posts
- **Cannot access**: End-to-end encrypted content, raw transaction data
- **Cannot do**: Determine legal privilege independently, decrypt communications
- **SLA**: 500 messages/second, <2000ms latency, 99.9% availability

### RU-001 Boundaries
- **Can access**: Regulatory feeds, enforcement databases, official gazettes
- **Cannot access**: Internal compliance policies (must request from orchestrator)
- **Cannot do**: Provide legal interpretations, modify compliance rules
- **SLA**: 50 updates/second, <5000ms latency, 99.5% availability

### RG-001 Boundaries
- **Can access**: All agent outputs, templates, audience profiles
- **Cannot access**: Raw source data directly (must use agent summaries)
- **Cannot do**: File reports without human authorization (dual sign-off)
- **SLA**: 10 reports/second, <10000ms latency, 99.5% availability

## 3. Inter-Agent Data Dependencies

| From | To | Data Type | Trigger |
|------|----|-----------|---------|
| TM-001 | ORCH-001 | DetectionAlert | Transaction anomaly detected |
| CS-001 | ORCH-001 | DetectionAlert | Communication violation detected |
| RU-001 | ORCH-001 | RegulatoryUpdate | New regulation published |
| ORCH-001 | TM-001 | Query | Request transaction lookup |
| ORCH-001 | CS-001 | Query | Request communication scan |
| ORCH-001 | RU-001 | Query | Request regulation check |
| ORCH-001 | RG-001 | ReportRequest | Consensus reached, report needed |
| RG-001 | ORCH-001 | Report | Report generated |
| ALL | ORCH-001 | Heartbeat | Every 30 seconds |
