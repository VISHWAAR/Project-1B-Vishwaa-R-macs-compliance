# Audit Trail

## Overview

The audit trail provides tamper-evident, cryptographically chained logging of all system events. It implements SEC Rule 17a-4(f) compliant immutability via SHA-256 hash chaining — each entry includes the hash of the previous entry, creating a blockchain-like chain where any modification to historical entries is immediately detectable.

**Module:** `observability/audit_trail.py`  
**Class:** `AuditTrail`  
**Singleton:** `get_audit_trail()`

## Design Principles

1. **Immutability** — Once written, entries cannot be modified (append-only)
2. **Completeness** — No gaps in the audit trail
3. **Authenticity** — Each entry is cryptographically hashed
4. **Temporal Integrity** — NTP-synchronized UTC timestamps
5. **Tamper Evidence** — SHA-256 hash chaining
6. **Reproducibility** — Same inputs → same audit trail (deterministic)

## Hash Chaining Mechanism

```
Entry 1: {data_1, previous_hash="GENESIS",        entry_hash=H1}
Entry 2: {data_2, previous_hash=H1,               entry_hash=H2}
Entry 3: {data_3, previous_hash=H2,               entry_hash=H3}
...
Entry N: {data_N, previous_hash=H(N-1),           entry_hash=HN}
```

The `previous_hash` of each entry is set to the `entry_hash` of the preceding entry. The first entry uses `"GENESIS"` as its previous hash.

### Canonical String for Hashing

Each `AuditEntry` is serialized to a canonical JSON string before hashing:

```python
def to_canonical_string(self) -> str:
    data = {
        "sequence_number": self.sequence_number,
        "timestamp": self.timestamp,
        "agent_id": self.agent_id,
        "event_type": self.event_type,
        "category": self.category,
        "severity": self.severity,
        "message": self.message,
        "trace_id": self.trace_id,
        "correlation_id": self.correlation_id,
        "payload": self.payload,
        "previous_hash": self.previous_hash,
    }
    return json.dumps(data, sort_keys=True, default=str)
```

The `sort_keys=True` ensures deterministic key ordering. The `default=str` handles datetime serialization. This canonical form is what gets SHA-256 hashed.

## AuditEntry Structure

```python
@dataclass
class AuditEntry:
    sequence_number: int          # Auto-incrementing
    timestamp: str                # ISO 8601 UTC
    agent_id: str                 # ORCH-001, TM-001, etc.
    event_type: str               # scenario.started, detection.INSIDER_TRADING, etc.
    category: str                 # agent_lifecycle, detection_event, escalation_event, etc.
    severity: str                 # INFO, ALERT, ERROR, CRITICAL, etc.
    message: str                  # Human-readable description
    trace_id: str                 # Distributed trace ID
    correlation_id: str           # Conversation correlation ID
    payload: Dict[str, Any]       # Additional structured context
    previous_hash: str            # Hash of previous entry (or "GENESIS")
    entry_hash: str               # SHA-256 of this entry's canonical string
    digital_signature: str        # Reserved for future cryptographic signing
```

## Integrity Verification

`AuditTrail.verify_integrity()` performs a complete chain audit:

```python
def verify_integrity(self) -> Dict[str, Any]:
    if not self._entries:
        return {"is_valid": True, "entries_checked": 0, "message": "Empty audit trail"}

    prev_hash = "GENESIS"
    for i, entry in enumerate(self._entries):
        # Check 1: Chain link integrity
        if entry.previous_hash != prev_hash:
            return {
                "is_valid": False,
                "entries_checked": i,
                "first_break": {
                    "sequence": entry.sequence_number,
                    "expected_prev_hash": prev_hash,
                    "actual_prev_hash": entry.previous_hash,
                },
                "message": f"Chain broken at entry #{entry.sequence_number}",
            }

        # Check 2: Hash recomputation
        computed_hash = entry.compute_hash()
        if computed_hash != entry.entry_hash:
            return {
                "is_valid": False,
                "entries_checked": i,
                "first_break": {
                    "sequence": entry.sequence_number,
                    "expected_hash": computed_hash,
                    "actual_hash": entry.entry_hash,
                },
                "message": f"Entry #{entry.sequence_number} has been tampered with",
            }

        prev_hash = entry.entry_hash

    return {
        "is_valid": True,
        "entries_checked": len(self._entries),
        "last_hash": self._last_hash,
        "message": "Audit trail integrity verified",
    }
```

Two checks per entry:
1. **Chain link:** Does `entry.previous_hash` match the hash we computed for the previous entry?
2. **Entry integrity:** Does recomputing `SHA256(canonical_string)` match `entry.entry_hash`?

## Event Types Logged

| Stage | Event Type | Category | Severity |
|-------|-----------|----------|----------|
| Scenario start | `scenario.started` | agent_lifecycle | INFO |
| Detection | `detection.{violation_type}` | detection_event | per detection severity |
| Consensus | `consensus.reached` | detection_event | INFO |
| Escalation created | `escalation.created` | escalation_event | ALERT |
| Scenario complete | `scenario.completed` | agent_lifecycle | INFO |

## Query API

```python
# Get all entries
get_entries()

# Filtered queries
get_entries(trace_id="trace-CS-01-...")
get_entries(agent_id="TM-001")
get_entries(category="detection_event")
get_entries(from_sequence=10, to_sequence=20)
get_entries(limit=100)

# Complete trace history
get_trace_history(trace_id="trace-CS-01-...")
```

## Export

```python
export_json(filepath)  # Exports all entries as JSON array
```

## Summary

```python
get_summary() → {
    "total_entries": 150,
    "sequence_range": (1, 150),
    "categories": {"agent_lifecycle": 40, "detection_event": 80, "escalation_event": 30},
    "chain_integrity": {"is_valid": True, ...},
    "first_entry": "2026-09-01T10:00:00Z",
    "last_entry": "2026-09-01T10:05:00Z",
}
```

## Retention

Audit entries inherit their retention period from the `AuditClassification` of the associated message or the event category:
- Regulatory events: 7-10 years
- Operational events: 5 years
- Diagnostic events: 1 year (rolling)

## Implementation

See `observability/audit_trail.py` — `AuditTrail`, `AuditEntry`, `get_audit_trail()`, `verify_integrity()`, `append()`, `export_json()`.
