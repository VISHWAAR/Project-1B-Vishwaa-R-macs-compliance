# CS-19: Multi-Jurisdiction Regulatory Conflict

**Scenario ID:** CS-19
**Agents Required:** RU
**Complexity:** High
**Expected Alert:** HIGH
**Applicable Regulations:** EMIR Reporting Obligation, MAS Securities and Futures Act, GDPR

---

## 1. Scenario Description

A new EU regulation mandates reporting of all OTC derivative transactions within 1 business day. Simultaneously, a Singapore regulation restricts cross-border sharing of client derivative position data. The firm has EU clients with Singapore-booked positions.

---

## 2. Signal Detection

### 2.1 Regulatory Update Tracker (RU-0001)

**Detection:** Cross-jurisdictional regulatory conflict

**Analysis:**
- EU: EMIR requires OTC derivative reporting within 1 business day
- Singapore: MAS restricts cross-border sharing of derivative position data
- Firm has EU clients with Singapore-booked positions
- Compliance with one regulation may violate the other

**Confidence:** 0.80

```json
{
  "violation_type": "REGULATORY_CHANGE",
  "severity": "HIGH",
  "confidence": 0.80,
  "description": "Cross-jurisdictional conflict: EU EMIR reporting vs Singapore data sharing restrictions",
  "evidence": [
    {"source": "cross_regulation_analysis", "description": "EU and Singapore regulations create contradictory obligations"},
    {"source": "client_book_analysis", "description": "EU clients have Singapore-booked derivative positions"}
  ],
  "regulations": ["EMIR Reporting Obligation", "MAS Securities and Futures Act", "GDPR"],
  "jurisdictions": ["EU", "Singapore"]
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
**Escalation:** HIGH + cross-jurisdictional → Tier 2 (Senior Analyst) — requires legal counsel engagement

**Resolution Required:**
1. Engage legal counsel for both jurisdictions
2. Assess whether reporting exemptions exist
3. Determine if data localization can satisfy both requirements
4. Document compliance analysis for regulatory examination

---

## 4. Audit Trail
| # | Event | Agent | Severity |
|---|-------|-------|----------|
| 1 | scenario.started | ORCH-001 | INFO |
| 2 | detection.regulatory_change | RU-001 | HIGH |
| 3 | consensus.reached | ORCH-001 | INFO |
| 4 | escalation.created (Tier 2) | ORCH-001 | ALERT |
| 5 | report.generated (×5) | RG-001 | INFO |
| 6 | scenario.completed | ORCH-001 | INFO |
