# CS-10: Front-Running — Client Order Anticipation

**Scenario ID:** CS-10
**Agents Required:** TM
**Complexity:** Medium
**Expected Alert:** CRITICAL
**Applicable Regulations:** SEC Section 17(j), Investment Company Act Section 17(j), FINRA Rule 5270

---

## 1. Scenario Description

A trader consistently executes personal account trades 10–30 minutes before large client orders in the same securities. Over 3 months, 89% of personal trades are profitable with 2.3% average return.

---

## 2. Signal Detection

### 2.1 Transaction Monitor (TM-001)

**Detection:** Front-running pattern — personal trades systematically precede client orders

**Pattern Analysis:**
- 79 out of 89 personal trades executed before client orders (89% correlation)
- Average 20 minutes before client order
- 89% profit rate on personal trades (threshold: 80%)
- 2.3% average return per trade

**Confidence:** 0.90

```json
{
  "violation_type": "FRONT_RUNNING",
  "severity": "CRITICAL",
  "confidence": 0.90,
  "description": "Front-running detected: 79/89 personal trades before client orders, 89% profit rate, 2.3% avg return",
  "evidence": [
    {"source": "order_sequence_analysis", "description": "89% of personal trades precede client orders by avg 20 min"}
  ],
  "regulations": ["SEC Section 17(j)", "FINRA Rule 5270"],
  "jurisdictions": ["US"]
}
```

---

## 3. Consensus

```json
{
  "TM-001": {"detected": true, "confidence": 0.90, "severity": "CRITICAL"},
  "CS-001": {"detected": false, "confidence": 0.30, "severity": "LOW"},
  "RU-001": {"detected": false, "confidence": 0.30, "severity": "LOW"}
}
```

**Combined:** 0.5946 → DETECT
**Escalation:** CRITICAL → Tier 3 (Manager)

---

## 4. Audit Trail
| # | Event | Agent | Severity |
|---|-------|-------|----------|
| 1 | scenario.started | ORCH-001 | INFO |
| 2 | detection.front_running | TM-001 | CRITICAL |
| 3 | consensus.reached | ORCH-001 | INFO |
| 4 | escalation.created (Tier 3) | ORCH-001 | ALERT |
| 5 | report.generated (×5) | RG-001 | INFO |
| 6 | scenario.completed | ORCH-001 | INFO |
