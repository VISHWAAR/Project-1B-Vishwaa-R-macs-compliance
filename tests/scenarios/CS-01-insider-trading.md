# CS-01: Insider Trading — Pre-Announcement Accumulation

**Scenario ID:** CS-01
**Agents Required:** TM + CS
**Complexity:** High
**Expected Alert:** CRITICAL
**Applicable Regulations:** SEC Rule 10b-5, FINRA Rule 2010, Insider Trading Sanctions Act

---

## 1. Scenario Description

A portfolio manager accumulates significant positions in Company X shares over 3 weeks. Internal emails reveal the PM attended a private dinner with Company X's CFO 4 weeks ago. Company X announces an acquisition 2 days after the last purchase, causing a 35% price increase.

---

## 2. Signal Detection

### 2.1 Transaction Monitor (TM-001)

**Detection Signal:** Unusual accumulation pattern in COMPANY_X shares

**Pattern Analysis:**
- 21 buy transactions over 3 weeks (above 95th percentile for this account)
- Average position size: $500,000 per transaction
- Total accumulation: ~$10.5M over 21 days
- Account type: Personal (not fund account)

**Confidence Score:** 0.85

**Methodology:**
```
accumulation_score = (trade_count / expected_count) × (position_percentile / 100)
= (21 / 5) × (95 / 100)
= 4.2 × 0.95 = 3.99 → normalized to 0.85
```

**Detection Event:**
```json
{
  "violation_type": "INSIDER_TRADING",
  "severity": "CRITICAL",
  "confidence": 0.85,
  "description": "Pre-announcement accumulation: 21 buy orders over 21 days totaling $10.5M in COMPANY_X",
  "evidence": [
    {
      "source": "transaction_log",
      "description": "Unusual accumulation pattern over 21 days before acquisition announcement",
      "data": {"days_before": 18, "price_change_pct": 35.0},
      "confidence": 0.85
    }
  ]
}
```

### 2.2 Communication Scanner (CS-001)

**Detection Signal:** Communication link between PM and Company X CFO

**Analysis:**
- Email/communication records show PM attended private dinner with CFO
- Timing: 4 weeks before acquisition announcement
- Channel: Private dinner (detected via calendar integration + expense records)

**Confidence Score:** 0.75

**Detection Event:**
```json
{
  "violation_type": "INSIDER_TRADING",
  "severity": "CRITICAL",
  "confidence": 0.75,
  "description": "Communication link: PM attended private dinner with Company X CFO 4 weeks before announcement",
  "evidence": [
    {
      "source": "communication_scan",
      "description": "Calendar/expense records show PM-CFO meeting",
      "data": {"meeting_date": "2024-12-15", "channel": "private_dinner"},
      "confidence": 0.75
    }
  ]
}
```

---

## 3. Inter-Agent Communication

### 3.1 TM → ORCH: ALERT Message

```json
{
  "message_id": "MSG-001-TM",
  "message_type": "ALERT",
  "priority": 1,
  "sender_agent_id": "TM-001",
  "recipient_agent_id": "ORCH-001",
  "payload_schema": "detection.insider_trading.v1",
  "confidence_score": 0.85,
  "audit_classification": "REGULATORY"
}
```

### 3.2 CS → ORCH: ALERT Message

```json
{
  "message_id": "MSG-002-CS",
  "message_type": "ALERT",
  "priority": 1,
  "sender_agent_id": "CS-001",
  "recipient_agent_id": "ORCH-001",
  "payload_schema": "detection.insider_trading.v1",
  "confidence_score": 0.75,
  "audit_classification": "REGULATORY"
}
```

---

## 4. Consensus Resolution

### 4.1 Agent Assessments

```json
{
  "TM-001": {"detected": true, "confidence": 0.85, "severity": "CRITICAL"},
  "CS-001": {"detected": true, "confidence": 0.75, "severity": "CRITICAL"},
  "RU-001": {"detected": false, "confidence": 0.30, "severity": "LOW"}
}
```

### 4.2 Bayesian Consensus

```
Prior: P(H) = 0.3

TM evidence: LR = 1 + 0.85 × 9 = 8.65
  odds(H) = 0.3/0.7 = 0.4286
  odds(H|TM) = 8.65 × 0.4286 = 3.707
  P(H|TM) = 3.707 / 4.707 = 0.7874

CS evidence: LR = 1 + 0.75 × 9 = 7.75
  odds(H|TM) = 3.707
  odds(H|TM,CS) = 7.75 × 3.707 = 28.73
  P(H|TM,CS) = 28.73 / 29.73 = 0.9664

RU evidence (not detected): LR = 1 / (1 + 0.30 × 9) = 0.2703
  odds(H|TM,CS) = 28.73
  odds(H|TM,CS,RU) = 0.2703 × 28.73 = 7.766
  P(H|TM,CS,RU) = 7.766 / 8.766 = 0.8860

Bayesian Posterior: 0.8860
```

### 4.3 Dempster-Shafer

```
TM belief: m({True}) = 0.85, m(Θ) = 0.15
CS belief: m({True}) = 0.75, m(Θ) = 0.25

Combined: m({True}) ≈ 0.9634
DS Belief Violation: 0.9634
```

### 4.4 Final Consensus

```
Combined = 0.4 × 0.8860 + 0.3 × 0.9634 + 0.3 × 0.85 = 0.8979
Decision: DETECT
Confidence: 0.8979
Conflict Level: low (both agents agree)
```

---

## 5. Escalation Decision

### 5.1 Triggers Activated
- ✅ HIGH_CONFIDENCE_DETECTION (confidence 0.85 > 0.8 threshold)
- ✅ CRITICAL_SEVERITY
- ✅ MULTI_AGENT_CONFLICT (TM detects, RU doesn't)

### 5.2 Tier Assignment
CRITICAL severity → **Tier 3 (Compliance Manager)**

### 5.3 Decision Support Package
```
Detection: Insider Trading — Pre-Announcement Accumulation
Severity: CRITICAL
Confidence: 89.8%
Agents Reporting: 2/3 (TM + CS agree, RU not applicable)
Evidence: Transaction pattern + communication link
Regulations: SEC Rule 10b-5, FINRA Rule 2010
Recommended Actions:
  1. Immediately investigate and preserve evidence
  2. Freeze PM's trading account
  3. Prepare SAR filing
  4. Notify Legal and Compliance Director
SLA: 4 hours for initial response
```

---

## 6. Report Generation

**5 reports generated** for audiences: Operations, Management, Board, Regulator, Auditor

**Key Report Elements:**
- Executive summary with detection count and severity
- Transaction timeline with evidence
- Communication evidence with source attribution
- Regulatory citations
- Escalation status and SLA

---

## 7. Audit Trail

| # | Event | Agent | Severity |
|---|-------|-------|----------|
| 1 | scenario.started | ORCH-001 | INFO |
| 2 | detection.insider_trading | TM-001 | CRITICAL |
| 3 | detection.insider_trading | CS-001 | CRITICAL |
| 4 | consensus.reached | ORCH-001 | INFO |
| 5 | escalation.created | ORCH-001 | ALERT |
| 6 | report.generated | RG-001 | INFO (×5) |
| 7 | scenario.completed | ORCH-001 | INFO |

All entries linked via trace_id, SHA-256 hash-chained for tamper evidence.
