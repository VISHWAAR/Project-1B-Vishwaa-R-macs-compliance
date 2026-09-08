# Logging Taxonomy & Structured Log Schema

**Version:** 1.0.0

---

## 1. Log Categories

| Category | Severity Levels | Retention | Example Events |
|----------|----------------|-----------|----------------|
| Agent Lifecycle | INFO, WARN, ERROR, FATAL | 7 years | Startup, shutdown, health check, config change |
| Detection Events | INFO, WARN, ALERT, CRITICAL | 7 years (10 for SAR) | Pattern detection, threshold breach, anomaly ID |
| Communication Events | DEBUG, INFO, WARN, ERROR | 5 years | Message sent, received, acknowledged, timeout |
| Escalation Events | INFO, WARN, ALERT | 7 years | Escalation triggered, assigned, resolved, overridden |
| Human Decision Events | INFO, ALERT | 10 years | Review initiated, decision made, rationale documented |
| Report Generation | INFO, WARN, ERROR | 7 years | Report triggered, validated, distributed, filed |
| System Performance | DEBUG, INFO, WARN | 1 year (rolling) | Throughput, latency, queue depths, resource utilisation |
| Security Events | WARN, ALERT, CRITICAL | 7 years | Authentication, authorization, access denied, data access |

## 2. Structured Log Schema

Every log entry is a JSON object with:

```json
{
  "entry_id": "detection_event-000042",
  "timestamp": "2026-09-05T14:30:00.000Z",
  "category": "detection_event",
  "severity": "CRITICAL",
  "agent_id": "TM-001",
  "event_type": "detection.insider_trading",
  "message": "Pre-announcement accumulation detected",
  "trace_id": "trace-CS-01-1693929000",
  "correlation_id": "MSG-001-TM",
  "payload": {
    "violation_type": "INSIDER_TRADING",
    "confidence": 0.85,
    "evidence_count": 2
  },
  "duration_ms": 3.2,
  "previous_hash": "a1b2c3...",
  "entry_hash": "d4e5f6..."
}
```

## 3. Tamper-Evidence Mechanism

Each log entry includes:
1. **previous_hash**: SHA-256 hash of the previous entry
2. **entry_hash**: SHA-256 hash of this entry's canonical string representation

Verification: Recompute each entry's hash and verify it matches the stored hash, and that each entry's previous_hash matches the previous entry's entry_hash.

## 4. Implementation

- **Logger:** `observability/logger.py` — StructuredLogger class
- **Audit Trail:** `observability/audit_trail.py` — AuditTrail class with hash chaining
- **Dashboard:** `observability/dashboard.py` — 3-panel ComplianceDashboard
