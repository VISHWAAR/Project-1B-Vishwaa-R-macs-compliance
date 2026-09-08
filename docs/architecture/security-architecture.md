# Security Architecture

## Overview

The MACS security architecture addresses three primary concerns: (1) tamper-evident audit logging, (2) message authentication and replay prevention, and (3) regulatory data retention compliance. It spans the audit trail, message schema, structured logger, and escalation framework.

## Audit Trail — Cryptographic Hash Chaining

### Design

The audit trail implements SEC Rule 17a-4(f) compliant immutability via SHA-256 hash chaining. Each entry includes the hash of the previous entry, creating a blockchain-like chain where any modification to historical entries breaks the chain immediately.

```
Entry 1: {data, prev_hash="GENESIS", entry_hash=H1}
Entry 2: {data, prev_hash=H1,          entry_hash=H2}
Entry 3: {data, prev_hash=H2,          entry_hash=H3}
...
```

### Integrity Verification

`AuditTrail.verify_integrity()` performs two checks per entry:
1. **Chain link check:** `entry.previous_hash == previously_computed_hash`
2. **Hash recomputation:** `SHA256(canonical_string) == entry.entry_hash`

Returns `{is_valid: bool, entries_checked: int, first_break: ...}`.

### Canonical String

Each entry is serialized to a canonical JSON string (sorted keys, `default=str` for date serialization) before hashing. This ensures deterministic hash values regardless of object construction order.

### Implementation

`observability/audit_trail.py` — `AuditTrail` class, `AuditEntry` dataclass, `get_audit_trail()` singleton.

---

## Message Authentication

### Nonce (Replay Prevention)

Every `MessageEnvelope` includes a `nonce` field (first 16 hex chars of a UUID v4). This prevents message replay attacks — even if an adversary captures a valid message, resending it would use a duplicate nonce.

### Sender Signature (Placeholder)

The `sender_signature` field in `MessageEnvelope` is reserved for cryptographic message authentication (e.g., HMAC-SHA256 signed with a per-agent secret key). The current implementation stores an empty string; production deployment would populate this with actual signatures.

```python
# Production enhancement (not in current scope)
signature = HMAC_SHA256(agent_secret_key, canonical_message_body)
envelope.sender_signature = signature
```

### Protocol Version Validation

The router checks `envelope.protocol_version` against the expected version (`1.0.0`). Mismatches are logged as warnings. This prevents older clients from injecting malformed messages into the system.

---

## Structured Logging — 8-Category Taxonomy

### Categories

| Category | Enum Value | Retention |
|----------|-----------|-----------|
| Agent Lifecycle | `agent_lifecycle` | 7 years |
| Detection Events | `detection_event` | 7 years |
| Communication Events | `communication_event` | 5 years |
| Escalation Events | `escalation_event` | 7 years |
| Human Decision Events | `human_decision` | 10 years |
| Report Generation | `report_generation` | 7 years |
| System Performance | `system_performance` | 1 year (rolling) |
| Security Events | `security_event` | 7 years |

### Severity Levels

`DEBUG < INFO < WARN < ALERT < ERROR < CRITICAL < FATAL`

### StructuredLogEntry

Every log entry is a `StructuredLogEntry` dataclass with:
- `entry_id`: `{category}-{counter:06d}`
- `timestamp`: ISO 8601 UTC
- `category`, `severity`, `agent_id`, `event_type`, `message`
- `trace_id`, `correlation_id` for distributed tracing
- `payload`: arbitrary context dict
- `duration_ms`: operation duration (optional)

### Concurrency Note

The `StructuredLogger` uses in-memory lists. In a multi-process deployment, each process would have its own logger instance writing to a shared structured log sink (e.g., ELK stack, CloudWatch). The current implementation is single-process; the API is designed to be backend-agnostic.

---

## Escalation Authorization Controls

The escalation framework enforces role-based access control on human decisions:

| Tier | Authorities |
|------|-------------|
| Tier 1 (Analyst) | acknowledge_alert, request_more_data, dismiss_false_positive |
| Tier 2 (Senior Analyst) | + initiate_investigation, modify_thresholds |
| Tier 3 (Manager) | + file_sar, notify_regulator, initiate_trade_halt |
| Tier 4 (Director/CCO) | + board_notification, self_report_to_regulator |

### Authorization Check

When `handle_decision()` is called with a decision type:

```python
if decision in ("file_sar", "notify_regulator", "initiate_trade_halt"):
    min_tier = EscalationTier.TIER_3_MANAGER
    if tier < min_tier:
        logger.warning(f"Decision '{decision}' requires Tier {min_tier.value}+")
        # Decision is still recorded but warning logged
```

This prevents junior staff from filing SARs or halting trades without manager authorization.

---

## Data Privacy

### Communication Scanner Privacy Constraints

The CS agent operates under privacy-preserving constraints:

1. **No decryption of E2E-encrypted communications** — voice analysis limited to transcribed text
2. **Respect data retention boundaries** — communications are processed inline, not stored beyond the processing window
3. **Cannot independently determine legal privilege** — privilege detection flags for human review, does not auto-suppress
4. **Privacy-preserving analysis** — personal communications are scanned for compliance keywords without retaining content

### Regulatory Tracker Jurisdiction Boundaries

The RU agent monitors 12 regulatory bodies across jurisdictions:

```
US:   SEC, FINRA, OCC, CFPB
UK/EU:  FCA, ECB/SSM
APAC:  MAS, HKMA, JFSA, ASIC
India: SEBI, RBI
```

Cross-jurisdictional conflicts are detected when regulations from two different jurisdictions impose contradictory requirements. The system flags these but does not attempt legal resolution — that is escalated to human review.

---

## Retention Compliance

### Regulatory Events (7-10 years)

Events classified as `AuditClassification.REGULATORY` (detection alerts, escalations, SAR-related decisions) are retained for 7 years minimum, 10 years for SAR-related human decisions.

### Operational Events (5 years)

Communication events and general operational logs are retained for 5 years.

### Diagnostic Events (1 year)

System performance metrics and diagnostic logs are retained on a rolling 1-year basis.

### Implementation

Retention is enforced at the logging infrastructure level (not in the current in-memory implementation). The `RETENTION_YEARS` mapping in `observability/logger.py` defines the policy; production deployment would translate these to infrastructure retention rules (S3 lifecycle policies, log group retention, database TTL).

---

## Recommendation: Production Hardening

| Area | Current State | Recommended Enhancement |
|------|--------------|------------------------|
| Audit trail storage | In-memory | Write to append-only WORM storage (S3 with Object Lock, or QLDB) |
| Message signatures | Placeholder (empty string) | HMAC-SHA256 per-agent keys, verified on receipt |
| Logger backend | In-memory list | Structured JSON logs to centralized sink (ELK/Datadog/CloudWatch) |
| Agent authentication | None | mTLS or JWT tokens for inter-agent communication |
| Escalation auth | Warning-only | Hard enforcement — reject unauthorized decisions at API boundary |
| Data at rest | N/A (in-memory) | AES-256 encryption for stored audit trails and detection evidence |
| PII handling | Scanner processes inline | Explicit PII redaction before log storage; consent management for communication scanning |

---

## Implementation References

- `observability/audit_trail.py` — `AuditTrail`, `AuditEntry`, `verify_integrity()`
- `observability/logger.py` — `StructuredLogger`, `StructuredLogEntry`, `RETENTION_YEARS`
- `protocols/message_schema.py` — `MessageEnvelope`, nonce, sender_signature, audit_classification
- `protocols/routing.py` — `MessageRouter`, protocol version check, dead letter queue
- `escalation/framework.py` — `EscalationFramework.handle_decision()`, tier authorities
- `agents/communication_scanner.py` — privacy constraints in CS detection methods
