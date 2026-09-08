# CS-16: Conflict of Interest — Research Independence

**Scenario ID:** CS-16
**Agents Required:** CS + TM
**Complexity:** High
**Expected Alert:** CRITICAL
**Applicable Regulations:** SEC Regulation AC, FINRA Rule 2241, Global Research Settlement

---

## 1. Scenario Description

A research analyst changes a stock rating from 'sell' to 'buy' three days before the investment banking division launches a secondary offering for the same company. Emails show the analyst met with the IB team twice that week.

---

## 2. Signal Detection

### 2.1 Communication Scanner (CS-001)

**Detection 1: Chinese Wall Breach**
- Research analyst met with IB team twice in the week before rating change
- Cross-department communication detected

**Confidence:** 0.85

```json
{
  "violation_type": "CHINESE_WALL_BREACH",
  "severity": "CRITICAL",
  "confidence": 0.85,
  "description": "Research independence compromised: analyst met with IB team 2x before rating change ahead of secondary offering",
  "evidence": [
    {"source": "communication_scan", "description": "Research-IB meetings detected in week before rating change"},
    {"source": "calendar_analysis", "description": "2 meetings between RA and IB team"}
  ],
  "regulations": ["SEC Regulation AC", "FINRA Rule 2241", "Global Research Settlement"],
  "jurisdictions": ["US"]
}
```

### 2.2 Transaction Monitor (TM-001)

**Detection 2: Timing Anomaly**
- Rating change (sell→buy) 3 days before secondary offering
- Pattern consistent with research independence violation

**Confidence:** 0.78

```json
{
  "violation_type": "RESEARCH_INDEPENDENCE",
  "severity": "CRITICAL",
  "confidence": 0.78,
  "description": "Rating upgrade 3 days before secondary offering launch — suspicious timing pattern"
}
```

---

## 3. Consensus

```json
{
  "TM-001": {"detected": true, "confidence": 0.78, "severity": "CRITICAL"},
  "CS-001": {"detected": true, "confidence": 0.85, "severity": "CRITICAL"},
  "RU-001": {"detected": false, "confidence": 0.30, "severity": "LOW"}
}
```

**Bayesian:** Posterior = 0.9724 (two agents detect with high confidence)
**DS Belief:** 0.9856
**Combined:** 0.8876 → DETECT

**Escalation:** CRITICAL + multi-agent agreement → Tier 4 (Director/CCO)

---

## 4. Audit Trail
| # | Event | Agent | Severity |
|---|-------|-------|----------|
| 1 | scenario.started | ORCH-001 | INFO |
| 2 | detection.chinese_wall_breach | CS-001 | CRITICAL |
| 3 | detection.research_independence | TM-001 | CRITICAL |
| 4 | consensus.reached | ORCH-001 | INFO |
| 5 | escalation.created (Tier 4) | ORCH-001 | ALERT |
| 6 | report.generated (×5) | RG-001 | INFO |
| 7 | scenario.completed | ORCH-001 | INFO |
