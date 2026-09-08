# CS-15: Best Execution Failure — Systematic Order Routing Bias

**Scenario ID:** CS-15
**Agents Required:** TM
**Complexity:** Medium
**Expected Alert:** HIGH
**Applicable Regulations:** SEC Rule 606, FINRA Rule 5310, MiFID II Best Execution

---

## 1. Scenario Description

Analysis of 90 days of equity order routing data reveals 78% of marketable orders routed to a single payment-for-order-flow venue despite 3 other venues consistently offering better prices by 0.5–1.5 cents per share.

---

## 2. Signal Detection

### 2.1 Transaction Monitor (TM-001)

**Detection:** Systematic best execution failure

**Analysis:**
- 78% of orders routed to single venue (threshold: 70%)
- 3 other venues offer better prices (0.5-1.5¢/share improvement)
- Pattern persists over 90 days

**Confidence:** 0.82

```json
{
  "violation_type": "BEST_EXECUTION_FAILURE",
  "severity": "HIGH",
  "confidence": 0.82,
  "description": "Systematic best execution failure: 78% routed to single venue, 3 better-priced alternatives available",
  "evidence": [
    {"source": "order_routing_analysis", "description": "90-day routing analysis shows systematic bias"}
  ],
  "regulations": ["SEC Rule 606", "FINRA Rule 5310", "MiFID II Best Execution"],
  "jurisdictions": ["US", "EU"]
}
```

---

## 3. Consensus

```json
{
  "TM-001": {"detected": true, "confidence": 0.82, "severity": "HIGH"},
  "CS-001": {"detected": false, "confidence": 0.30, "severity": "LOW"},
  "RU-001": {"detected": false, "confidence": 0.30, "severity": "LOW"}
}
```

**Combined:** 0.612 → DETECT
**Escalation:** HIGH + cross-jurisdictional → Tier 2 (Senior Analyst)

---

## 4. Audit Trail
| # | Event | Agent | Severity |
|---|-------|-------|----------|
| 1 | scenario.started | ORCH-001 | INFO |
| 2 | detection.best_execution_failure | TM-001 | HIGH |
| 3 | consensus.reached | ORCH-001 | INFO |
| 4 | escalation.created (Tier 2) | ORCH-001 | ALERT |
| 5 | report.generated (×5) | RG-001 | INFO |
| 6 | scenario.completed | ORCH-001 | INFO |
