# Report Generator Agent (RG-001)

## Overview

The Report Generator compiles, formats, and distributes compliance reports for multiple stakeholder audiences. It supports scheduled reports, event-triggered reporting (SAR/STR), multi-audience adaptation, evidence compilation with source attribution, and regulatory filing preparation.

**Agent ID:** RG-001  
**Module:** `agents/report_generator.py`  
**Class:** `ReportGenerator`

## Audience Profiles

The agent adapts report detail and format based on the target audience:

| Audience | Detail Level | Format | Includes |
|----------|-------------|--------|----------|
| Board (`board`) | High-level | Executive summary | Regulatory citations, financial impact; no technical details |
| Management (`management`) | Moderate | Management briefing | Regulatory citations, financial impact; no technical details |
| Operations (`operations`) | Detailed | Operational report | Full technical details, regulatory citations, evidence |
| Regulator (`regulator`) | Comprehensive | Regulatory filing | Full details, evidence package, audit trail summary |
| Auditor (`auditor`) | Comprehensive | Audit evidence | Full details, evidence package, audit trail summary |

## Report Sections

Every report includes sections based on audience detail level:

### All Audiences
1. **Executive Summary** — Total detections, severity breakdown, consensus decision, overall confidence, conflict level

### Detailed+ Audiences (operations, regulator, auditor)
2. **Detection Details** — Per-detection breakdown with violation type, severity, confidence, description, agent ID, regulations, jurisdictions, evidence, latency

### Comprehensive Audiences (regulator, auditor)
3. **Evidence Package** — All evidence items with source attribution, detection ID, violation type, description, confidence, timestamp, raw data
4. **Audit Trail Summary** — Total entries, chain integrity status, coverage statement, retention period

### All Audiences with Regulatory Citations Enabled
5. **Regulatory Analysis** — Applicable regulations (sorted), affected jurisdictions (sorted), regulatory implications

### If Escalation Exists
6. **Escalation Summary** — Escalation ID, current tier, triggered by, SLA deadline, recommended actions, human decision required, dual sign-off required

### All Audiences
7. **Recommendations** — Contextual actionable recommendations based on detection severity, conflict level, and escalation status

## Report Generation Flow

```python
generate_detection_report(
    detections,         # List of detection dicts from all agents
    consensus_result,   # Consensus engine output
    escalation,         # Optional escalation record
    audit_trail_entries,# Audit trail entries for this scenario
    audience,           # One of: operations, management, board, regulator, auditor
    scenario_id,        # e.g. "CS-01"
)
```

Returns a report dict with:
- `report_id`: `RPT-{scenario_id}-{audience_prefix}` (e.g. `RPT-CS-01-OPS`)
- `generated_at`: ISO 8601 UTC timestamp
- `audience`: Human-readable audience name
- `format`: Report format identifier
- `sections`: Dict of section name → section content
- `generation_time_ms`: Report generation latency

## SAR Draft Preparation

The `prepare_sar_draft()` method generates a Suspicious Activity Report draft for human review:

```python
def prepare_sar_draft(self, detection, evidence):
    return {
        "document_type": "SAR_DRAFT",
        "status": "pending_dual_sign_off",
        "filing_deadline": "30_days",
        "subject": detection["description"],
        "violation_type": detection["violation_type"],
        "sign_off_required": ["Compliance Officer", "MLRO"],
        "note": "AI-generated draft. Human review and sign-off required before filing."
    }
```

**Key constraint:** The agent cannot file regulatory reports without human authorization — dual sign-off (Compliance Officer + MLRO) is required.

## Constraints

- Cannot file regulatory reports without human authorisation (dual sign-off required)
- Report templates must be version-controlled
- Cannot include privileged materials without legal clearance
- Distribution lists are controlled

## Evidence Compilation

The `_build_evidence_package()` method compiles evidence from all detections with full source attribution:

```python
{
    "total_evidence_items": N,
    "evidence": [
        {
            "detection_id": "...",
            "violation_type": "...",
            "source": "transaction_log | email_scan | ...",
            "description": "...",
            "confidence": 0.85,
            "timestamp": "ISO-8601",
            "data": {...}
        },
        ...
    ],
    "source_attribution": "All evidence includes source agent and timestamp for audit trail"
}
```

## Regulatory Filing Preparation

The agent supports generating filing drafts in multiple formats (XBRL, XML, PDF) via the `regulatory_filing_preparation` capability. The current implementation provides the SAR draft preparation path; full filing format generation would be implemented with template-based document generation.

## Dependencies

- TM-001: Transaction Monitor (detection data)
- CS-001: Communication Scanner (detection data)
- RU-001: Regulatory Update Tracker (detection data, regulatory citations)

## Resource Requirements

| Resource | Value |
|----------|-------|
| CPU Cores | 2.0 |
| Memory | 1024 MB |
| Max Concurrent Tasks | 10 |
| SLA Throughput | 10 reports/sec |
| SLA Max Latency | 10000 ms |
| SLA Availability | 99.5% |

## Scenario Coverage

The report generator runs for all 20 scenarios, producing 5 audience-specific reports each (100 total reports across the full test suite). For CS-18 (false positive), reports reflect the NO_ALERT outcome with zero detections.

## Implementation

See `agents/report_generator.py` — `ReportGenerator` class, `generate_detection_report()`, `_build_*` section methods, `prepare_sar_draft()`, `AUDIENCE_PROFILES`.
