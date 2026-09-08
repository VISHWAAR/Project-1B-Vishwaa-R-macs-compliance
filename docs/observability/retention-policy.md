# Retention Policy

## Overview

The retention policy defines how long different categories of compliance data must be retained to meet regulatory obligations across all operating jurisdictions. These retention periods are enforced at the logging infrastructure level and apply to audit trail entries, detection events, escalation records, human decisions, and report archives.

**Module reference:** `observability/logger.py` — `RETENTION_YEARS` mapping

## Retention Periods by Category

| Log Category | Enum Value | Retention Period | Regulatory Basis |
|-------------|-----------|-----------------|-----------------|
| Agent Lifecycle | `agent_lifecycle` | 7 years | SEC Rule 17a-4, FINRA Rule 3110 |
| Detection Events | `detection_event` | 7 years | SEC Rule 17a-4, BSA/AML recordkeeping |
| Communication Events | `communication_event` | 5 years | SEC Rule 17a-4, MiFID II Article 16 |
| Escalation Events | `escalation_event` | 7 years | SEC Rule 17a-4, regulatory examination readiness |
| Human Decision Events | `human_decision` | 10 years | SAR-related decisions (10-year requirement), FINRA Rule 4511 |
| Report Generation | `report_generation` | 7 years | SEC Rule 17a-4, regulatory filing retention |
| System Performance | `system_performance` | 1 year (rolling) | Operational diagnostics, not regulatory |
| Security Events | `security_event` | 7 years | SEC Rule 17a-4, access audit requirements |

## Retention by Data Type

### Audit Trail Entries

Full retention follows the category of the originating event. Audit trail entries are cryptographically chained (SHA-256 hash chain) and must be retained as an unbroken chain for the full retention period. Any gap in the chain within the retention window is a compliance violation.

| Event Type | Retention |
|-----------|-----------|
| scenario.started / scenario.completed | 7 years |
| detection.* | 7 years |
| consensus.reached | 7 years |
| escalation.created / escalation.resolved | 7 years (10 years if SAR-related) |

### Detection Events and Evidence

All detection events, including the full evidence package (DetectionEvidence items with source data), must be retained for 7 years from the date of detection. This applies to both confirmed violations and false positives — the latter are important for calibrating detection thresholds and demonstrating the effectiveness of the false positive screening process.

### Escalation Records

Escalation records (EscalationRecord with full DecisionSupportPackage) must be retained for 7 years. If the escalation led to a SAR filing or regulatory notification, the retention extends to 10 years.

### Human Decisions

Human decision records (decision, rationale, decided_by, timestamp) must be retained for 10 years when they relate to SAR filings, regulatory notifications, or trade halts. Other human decisions (dismissals, threshold modifications) are retained for 7 years.

### Reports

All generated reports (executive summaries, operational reports, regulatory filings, audit evidence packages) must be retained for 7 years. SAR drafts and filed SARs are retained for 10 years.

### System Performance Metrics

Performance metrics (latency, throughput, queue depths, error rates) are retained on a rolling 1-year basis. These are operational diagnostics, not regulatory records, and are used for capacity planning and SLA monitoring.

## Jurisdictional Coverage

The retention policy covers requirements from:

| Jurisdiction | Key Regulation | Minimum Retention |
|-------------|----------------|-------------------|
| US (SEC) | Rule 17a-4 | 7 years (some records 6 years) |
| US (FINRA) | Rule 3110, Rule 4511 | 7 years (some records 6 years) |
| US (BSA/AML) | 31 CFR 1020.320 | 5 years (SARs: 5 years from filing) |
| EU | MiFID II Article 16 | 5-7 years (varies by record type) |
| UK | FCA SYSC, COBS | 5-7 years |
| India | SEBI, RBI guidelines | 5-8 years (varies) |

The policy adopts the **most stringent** applicable retention period for each category to ensure compliance across all jurisdictions where the institution operates.

## Storage Requirements

### Immutability

Regulatory records must be stored in a manner that prevents modification or deletion before the end of the retention period. This is typically achieved through:
- Append-only storage (WORM — Write Once Read Many)
- Cryptographic hash chaining (as implemented in the audit trail)
- Read-only access controls
- S3 Object Lock or equivalent in cloud storage

### Searchability

Records must be readily accessible and searchable for regulatory examinations. The retention policy must be implemented with indexing that allows:
- Retrieval by date range
- Retrieval by agent ID
- Retrieval by scenario ID / trace ID
- Retrieval by violation type
- Retrieval by severity

### Chain of Custody

For evidence packages and detection records, the chain of custody must be documented:
- What detected the event
- When it was detected
- What evidence was collected
- Who reviewed it (human decisions)
- What actions were taken (escalations, reports, filings)

## Disposal

At the end of the retention period, records may be disposed of in accordance with the institution's data disposal policy. Disposal must be:
- **Secure** — cryptographic erasure or physical destruction
- **Documented** — disposal log with date, records disposed, method
- **Approved** — compliance officer approval for regulatory record disposal

## Implementation Status

| Component | Status |
|-----------|--------|
| Retention policy defined (RETENTION_YEARS mapping) | ✅ Implemented in `observability/logger.py` |
| Audit trail hash chaining | ✅ Implemented in `observability/audit_trail.py` |
| Category-based retention tagging | ✅ Implemented via `AuditClassification` in message schema |
| Persistent storage with immutability | ⚠️ Design ready, not implemented (in-memory only) |
| Automated disposal scheduling | ❌ Not implemented |
| Regulatory examination export | ⚠️ Design ready (export_json available) |

## Implementation

See `observability/logger.py`:
- `RETENTION_YEARS: Dict[LogCategory, int]` — retention period mapping
- `StructuredLogEntry` — includes category for retention lookup
- `get_summary()` — reports retention policy

See `observability/audit_trail.py`:
- `AuditTrail.export_json()` — export for regulatory examination
- `AuditTrail.verify_integrity()` — chain integrity verification

See `protocols/message_schema.py`:
- `AuditClassification` enum — REGULATORY (7-10yr), OPERATIONAL (5yr), DIAGNOSTIC (1yr)
- `MessageEnvelope.audit_classification` — per-message retention classification
