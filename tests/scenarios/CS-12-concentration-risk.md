# CS-12: Concentration Risk — Portfolio Limit Breach

**Scenario ID:** CS-12
**Agents Required:** TM
**Complexity:** Low
**Expected Alert:** MEDIUM
**Applicable Regulations:** Investment Company Act Section 13, SEC Form N-PORT, UCITS concentration limits

---

## 1. Scenario Description

A fund manager's portfolio reaches 28% concentration in a single sector (limit: 25%) due to mark-to-market appreciation and new purchases, persisting for 5 trading days without corrective action.

---

## 2. Signal Detection

### 2.1 Transaction Monitor (TM-001)

**Detection:** Sector concentration limit breach

**Analysis:**
- Current concentration: 28% (limit: 25%)
- Breach persisting for 5 trading days
- Exceeded threshold by 3 percentage points

**Confidence:** 0.72

```json
{
  "violation_type": "CONCENTRATION_RISK",
  "severity": "MEDIUM",
  "confidence": 0.72,
  "description": "Concentration limit breach: 28% vs 25% limit, persisting for 5 days",
  "evidence": [
    {"source": "portfolio_analysis", "description": "Sector concentration 28% exceeds 25% limit for 5 days"}
  ],
  "regulations": ["Investment Company Act Section 13", "SEC Form N-PORT"],
  "jurisdictions": ["US", "EU"]
}
```

---

## 3. Consensus

```json
{
  "TM-001": {"detected": true, "confidence": 0.72, "severity": "MEDIUM"},
  "CS-001": {"detected": false, "confidence": 0.30, "severity": "LOW"},
  "RU-001": {"detected": false, "confidence": 0.30, "severity": "LOW"}
}
```

**Combined:** 0.6220 → DETECT
**Escalation:** MEDIUM severity → Tier 2 (Senior Analyst) — single-agent detection triggers multi-agent conflict review (consistent with CS-07)

---

## 4. Audit Trail
| # | Event | Agent | Severity |
|---|-------|-------|----------|
| 1 | scenario.started | ORCH-001 | INFO |
| 2 | detection.concentration_risk | TM-001 | MEDIUM |
| 3 | consensus.reached | ORCH-001 | INFO |
| 4 | escalation.created (Tier 2) | ORCH-001 | ALERT |
| 5 | report.generated (×5) | RG-001 | INFO |
| 6 | scenario.completed | ORCH-001 | INFO |
