# CS-06: Wash Trading — Cross-Account Coordination

**Scenario ID:** CS-06
**Agents Required:** TM
**Complexity:** High
**Expected Alert:** HIGH
**Applicable Regulations:** CEA Section 4c(a), SEC Rule 10b-5, FINRA Rule 5210

---

## 1. Scenario Description

Two accounts managed by different portfolio managers execute 34 matching trades in thinly traded corporate bonds over 2 weeks. Accounts alternate as buyer and seller with identical quantities and prices within 2 basis points.

---

## 2. Signal Detection

### 2.1 Transaction Monitor (TM-001)

**Detection:** Wash trading pattern — matching trades between related accounts

**Pattern Analysis:**
- 34 matching trades in thinly traded corporate bonds
- Two accounts alternate buyer/seller roles
- Identical quantities, prices within 2 bps (threshold: 5 bps)
- Over 14-day window

**Confidence:** 0.88

```json
{
  "violation_type": "WASH_TRADING",
  "severity": "HIGH",
  "confidence": 0.88,
  "description": "Suspected wash trading: 34 matching trades between 2 accounts, avg tolerance 2 bps, alternating sides",
  "evidence": [
    {"source": "cross_account_analysis", "description": "34 matching trades identified between ACCT-1 and ACCT-2"}
  ],
  "regulations": ["CEA Section 4c(a)", "SEC Rule 10b-5", "FINRA Rule 5210"],
  "jurisdictions": ["US"]
}
```

---

## 3. Consensus

```json
{
  "TM-001": {"detected": true, "confidence": 0.88, "severity": "HIGH"},
  "CS-001": {"detected": false, "confidence": 0.30, "severity": "LOW"},
  "RU-001": {"detected": false, "confidence": 0.30, "severity": "LOW"}
}
```

**Combined:** 0.5946 → DETECT
**Escalation:** HIGH severity + high confidence → Tier 2 (Senior Analyst)

---

## 4. Audit Trail
| # | Event | Agent | Severity |
|---|-------|-------|----------|
| 1 | scenario.started | ORCH-001 | INFO |
| 2 | detection.wash_trading | TM-001 | HIGH |
| 3 | consensus.reached | ORCH-001 | INFO |
| 4 | escalation.created (Tier 2) | ORCH-001 | ALERT |
| 5 | report.generated (×5) | RG-001 | INFO |
| 6 | scenario.completed | ORCH-001 | INFO |
