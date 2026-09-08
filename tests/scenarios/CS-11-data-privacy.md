# CS-11: Data Privacy Violation — Cross-Border Transfer

**Scenario ID:** CS-11
**Agents Required:** CS + RU
**Complexity:** Medium
**Expected Alert:** HIGH
**Applicable Regulations:** GDPR Articles 44–49, Schrems II ruling

---

## 1. Scenario Description

Customer account data for 14,000 EU residents is transferred to a server in a non-adequate jurisdiction without safeguards, consent, or Standard Contractual Clauses, as part of a routine system migration.

---

## 2. Signal Detection

### 2.1 Regulatory Update Tracker (RU-001)

**Detection:** Cross-jurisdictional regulatory conflict — GDPR data transfer rules

```json
{
  "violation_type": "DATA_PRIVACY_VIOLATION",
  "severity": "HIGH",
  "confidence": 0.80,
  "description": "GDPR cross-border data transfer: 14,000 EU resident records transferred without safeguards or SCCs",
  "evidence": [
    {"source": "cross_regulation_analysis", "description": "Transfer violates GDPR Articles 44-49 and Schrems II"}
  ],
  "regulations": ["GDPR Articles 44-49", "Schrems II ruling"],
  "jurisdictions": ["EU"],
  "requires_notification": true,
  "notification_deadline_hours": 72
}
```

---

## 3. Consensus

```json
{
  "TM-001": {"detected": false, "confidence": 0.30, "severity": "LOW"},
  "CS-001": {"detected": false, "confidence": 0.30, "severity": "LOW"},
  "RU-001": {"detected": true, "confidence": 0.80, "severity": "HIGH"}
}
```

**Combined:** 0.612 → DETECT
**Escalation:** HIGH + cross-jurisdictional → Tier 2 (Senior Analyst)

**Required Actions:**
1. Notify DPO within 72 hours
2. Assess regulatory breach notification requirements
3. Initiate data recall from non-adequate jurisdiction
4. Document transfer safeguards (or lack thereof)

---

## 4. Audit Trail
| # | Event | Agent | Severity |
|---|-------|-------|----------|
| 1 | scenario.started | ORCH-001 | INFO |
| 2 | detection.data_privacy_violation | RU-001 | HIGH |
| 3 | consensus.reached | ORCH-001 | INFO |
| 4 | escalation.created (Tier 2) | ORCH-001 | ALERT |
| 5 | report.generated (×5) | RG-001 | INFO |
| 6 | scenario.completed | ORCH-001 | INFO |
