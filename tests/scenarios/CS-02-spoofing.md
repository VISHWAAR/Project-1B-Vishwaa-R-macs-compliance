# CS-02: Market Manipulation — Spoofing in Futures Markets

**Scenario ID:** CS-02
**Agents Required:** TM
**Complexity:** Medium
**Expected Alert:** HIGH
**Applicable Regulations:** Dodd-Frank Act Section 747, CEA Section 4c(a)(5), CME Rule 575

---

## 1. Scenario Description

An algorithmic trading desk places large limit orders in crude oil futures consistently cancelled within 200–500 milliseconds. Orders placed on one side followed by rapid execution on the opposite side, occurring 47 times in a single session.

---

## 2. Signal Detection

### 2.1 Transaction Monitor (TM-001)

**Detection Signal:** Spoofing/layering pattern in order data

**Pattern Analysis:**
- 47 large limit orders placed and cancelled within 200-500ms
- Order cancel rate: 92% (threshold: 85%)
- Opposite-side executions: 38 out of 47 (81%)
- All in crude oil futures, single session

**Confidence Score:** 0.95

**Methodology:**
```
cancel_score = cancel_rate / threshold = 0.92 / 0.85 = 1.082 (exceeds)
timing_score = (500 - avg_lifetime) / (500 - 0) = (500-350)/500 = 0.3
opposite_score = opposite_executions / total = 38/47 = 0.809
confidence = min(0.95, 0.3 + 0.3 + 0.2 + 0.2) = 0.95 (all signals strong)
```

**Detection Event:**
```json
{
  "violation_type": "SPOOFING_LAYERING",
  "severity": "HIGH",
  "confidence": 0.95,
  "description": "Spoofing detected: 47 large orders cancelled within 350ms avg, 92% cancel rate, 38 opposite-side executions",
  "evidence": [
    {"source": "order_book_analysis", "description": "Order pattern: 47 large orders cancelled within 500ms"},
    {"source": "execution_analysis", "description": "38 opposite-side executions following cancellations"}
  ],
  "regulations": ["Dodd-Frank Act Section 747", "CEA Section 4c(a)(5)", "CME Rule 575"],
  "jurisdictions": ["US"]
}
```

### 2.2 Communication Scanner (CS-001)
**No communications flagged.** This is an algorithmic pattern, not communication-based.

### 2.3 Regulatory Update Tracker (RU-001)
**No regulatory updates** relevant.

---

## 3. Inter-Agent Communication

**Single agent scenario.** TM-001 sends ALERT to ORCH-001.

```
TM-001 ──ALERT (HIGH)──→ ORCH-001
```

---

## 4. Consensus Resolution

### 4.1 Agent Assessments
```json
{
  "TM-001": {"detected": true, "confidence": 0.95, "severity": "HIGH"},
  "CS-001": {"detected": false, "confidence": 0.30, "severity": "LOW"},
  "RU-001": {"detected": false, "confidence": 0.30, "severity": "LOW"}
}
```

### 4.2 Bayesian Consensus
```
TM evidence: LR = 1 + 0.95 × 9 = 9.55
  P(H|TM) = 0.9142

CS evidence (not detected): LR = 0.2703
  P(H|TM,CS) = 0.6670

RU evidence (not detected): LR = 0.2703
  P(H|TM,CS,RU) = 0.3501

Bayesian Posterior: 0.3501
```

### 4.3 Dempster-Shafer
```
TM: m({True}) = 0.95, m(Θ) = 0.05
CS: m({False}) = 0.30, m(Θ) = 0.70
Combined: m({True}) ≈ 0.5647
```

### 4.4 Final Consensus
```
Combined = 0.4 × 0.3501 + 0.3 × 0.5647 + 0.3 × 0.95 = 0.5946
Decision: DETECT (borderline — escalated due to high agent confidence)
```

---

## 5. Escalation Decision

**Trigger:** HIGH_CONFIDENCE_DETECTION (0.95 > 0.8)
**Tier:** HIGH severity → Tier 2 (Senior Analyst)

**Decision Support Package:**
```
Spoofing/layering in crude oil futures
Severity: HIGH | Confidence: 95%
47 cancelled orders, 38 opposite-side executions
Regulations: Dodd-Frank §747, CEA §4c(a)(5)
Recommended: Review trading desk algorithms, check for pattern across sessions
SLA: 1 hour
```

---

## 6. Audit Trail
| # | Event | Agent | Severity |
|---|-------|-------|----------|
| 1 | scenario.started | ORCH-001 | INFO |
| 2 | detection.spoofing_layering | TM-001 | HIGH |
| 3 | consensus.reached | ORCH-001 | INFO |
| 4 | escalation.created (Tier 2) | ORCH-001 | ALERT |
| 5 | report.generated (×5) | RG-001 | INFO |
| 6 | scenario.completed | ORCH-001 | INFO |
