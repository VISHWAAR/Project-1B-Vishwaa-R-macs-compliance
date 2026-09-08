# CS-04: AML — Structuring Deposits

**Scenario ID:** CS-04
**Agents Required:** TM
**Complexity:** Medium
**Expected Alert:** CRITICAL
**Applicable Regulations:** Bank Secrecy Act, 31 CFR 1020.320, FinCEN SAR requirements

---

## 1. Scenario Description

A commercial banking client makes 23 cash deposits over 10 business days, each between $8,500 and $9,900, at 7 different branches. Total deposits: $214,000.

---

## 2. Signal Detection

### 2.1 Transaction Monitor (TM-001)

**Detection:** Currency structuring (smurfing) pattern

**Pattern Analysis:**
- 23 cash deposits in 10 days
- All deposits between $8,500-$9,900 (just below $10,000 CTR threshold)
- 7 different branches used
- Total: $214,000
- 23/23 deposits in structuring range

**Confidence:** 0.92

```json
{
  "violation_type": "AML_STRUCTURING",
  "severity": "CRITICAL",
  "confidence": 0.92,
  "description": "Suspected currency structuring: 23 cash deposits totalling $214,000 across 7 branches, all just below $10K threshold",
  "evidence": [
    {"source": "transaction_log", "description": "23/23 deposits in $8,500-$9,900 range across 7 branches"}
  ],
  "regulations": ["Bank Secrecy Act", "31 CFR 1020.320", "FinCEN SAR requirements"],
  "jurisdictions": ["US"],
  "requires_sar": true
}
```

---

## 3. Consensus

```json
{
  "TM-001": {"detected": true, "confidence": 0.92, "severity": "CRITICAL"},
  "CS-001": {"detected": false, "confidence": 0.30, "severity": "LOW"},
  "RU-001": {"detected": false, "confidence": 0.30, "severity": "LOW"}
}
```

**Combined:** 0.5946 → DETECT
**Escalation:** CRITICAL severity → Tier 3 (Manager)
**SAR Required:** Yes — must file within 30 days

---

## 4. Report Generation

RG prepares SAR draft with:
- Subject: Suspected currency structuring
- Activity period: 10 business days
- Amount: $214,000
- Suspicious indicators: Multiple sub-threshold deposits across branches
- Sign-off required: Compliance Officer + MLRO

---

## 5. Audit Trail
| # | Event | Agent | Severity |
|---|-------|-------|----------|
| 1 | scenario.started | ORCH-001 | INFO |
| 2 | detection.aml_structuring | TM-001 | CRITICAL |
| 3 | consensus.reached | ORCH-001 | INFO |
| 4 | escalation.created (Tier 3) | ORCH-001 | ALERT |
| 5 | report.generated (×5) | RG-001 | INFO |
| 6 | scenario.completed | ORCH-001 | INFO |
