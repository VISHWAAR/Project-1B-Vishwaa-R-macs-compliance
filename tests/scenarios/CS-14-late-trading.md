# CS-14: Late Trading — Mutual Fund NAV Manipulation

**Scenario ID:** CS-14
**Agents Required:** TM
**Complexity:** Medium
**Expected Alert:** CRITICAL
**Applicable Regulations:** SEC Rule 22c-1, Investment Company Act Section 22(c)

---

## 1. Scenario Description

Order management system logs show 14 mutual fund purchase orders timestamped at 4:00:00 PM ET but with system entry timestamps of 4:12–4:23 PM ET, receiving same-day pricing.

---

## 2. Signal Detection

### 2.1 Transaction Monitor (TM-001)

**Detection:** Late trading — orders executed after NAV cutoff receiving same-day pricing

**Analysis:**
- 14 mutual fund purchase orders
- Order timestamp: 4:00:00 PM ET (NAV cutoff)
- System entry: 4:12-4:23 PM ET (12-23 minutes late)
- All received same-day NAV pricing

**Confidence:** 0.88

```json
{
  "violation_type": "LATE_TRADING",
  "severity": "CRITICAL",
  "confidence": 0.88,
  "description": "Late trading: 14 mutual fund orders entered 12-23 min after cutoff, received same-day pricing",
  "evidence": [
    {"source": "order_timestamp_analysis", "description": "System entry timestamps 12-23 min after NAV cutoff"}
  ],
  "regulations": ["SEC Rule 22c-1", "Investment Company Act Section 22(c)"],
  "jurisdictions": ["US"]
}
```

---

## 3. Consensus

```json
{
  "TM-001": {"detected": true, "confidence": 0.88, "severity": "CRITICAL"},
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
| 2 | detection.late_trading | TM-001 | CRITICAL |
| 3 | consensus.reached | ORCH-001 | INFO |
| 4 | escalation.created (Tier 3) | ORCH-001 | ALERT |
| 5 | report.generated (×5) | RG-001 | INFO |
| 6 | scenario.completed | ORCH-001 | INFO |
