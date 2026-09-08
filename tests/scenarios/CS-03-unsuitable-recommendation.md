# CS-03: Unsuitable Investment Recommendation

**Scenario ID:** CS-03
**Agents Required:** CS + TM
**Complexity:** High
**Expected Alert:** HIGH
**Applicable Regulations:** FINRA Rule 2111, SEC Regulation Best Interest

---

## 1. Scenario Description

A financial advisor recommends high-risk leveraged ETF products to 12 retirement account clients aged 68–82, describing them as 'safe income generators'. None of the clients' investment policy statements allow speculative instruments.

---

## 2. Signal Detection

### 2.1 Communication Scanner (CS-001)

**Detection 1: Misleading Language**
- Keywords found: "safe income generators" (in MISLEADING_KEYWORDS list)
- 12 client-facing communications with misleading claims

**Confidence:** 0.80

```json
{
  "violation_type": "SUITABILITY_VIOLATION",
  "severity": "HIGH",
  "confidence": 0.80,
  "description": "Misleading investment recommendation: leveraged ETFs described as 'safe income generators' to 12 retirement clients aged 68-82",
  "evidence": [
    {"source": "keyword_scan", "description": "Misleading keywords found in 12 client communications"},
    {"source": "client_profile", "description": "All 12 clients are retirement accounts with conservative IPS"}
  ],
  "regulations": ["FINRA Rule 2111", "SEC Reg BI"],
  "jurisdictions": ["US"]
}
```

### 2.2 Transaction Monitor (TM-001)
**No transaction anomalies detected** — the issue is suitability, not transaction patterns.

---

## 3. Inter-Agent Communication

```
CS-001 ──ALERT (HIGH)──→ ORCH-001
```

---

## 4. Consensus Resolution

```json
{
  "TM-001": {"detected": false, "confidence": 0.30, "severity": "LOW"},
  "CS-001": {"detected": true, "confidence": 0.80, "severity": "HIGH"},
  "RU-001": {"detected": false, "confidence": 0.30, "severity": "LOW"}
}
```

**Bayesian Posterior:** 0.3947 (moderate — single agent detects)
**DS Belief:** 0.4821
**Combined:** 0.4 × 0.3947 + 0.3 × 0.4821 + 0.3 × 0.80 = **0.5355**
**Decision:** DETECT (escalated via any_agent_detected trigger)

---

## 5. Escalation

**Trigger:** CRITICAL language toward elderly clients + HIGH confidence
**Tier:** Tier 4 (Director/CCO) — elderly client exploitation risk

**Decision Support:**
```
Suitability violation affecting 12 vulnerable retirement clients
FINRA Rule 2111: Know Your Customer, suitability obligation
SEC Reg BI: Best interest standard for retail recommendations
Recommended: Freeze advisory account, notify compliance, prepare client remediation
```

---

## 6. Audit Trail
| # | Event | Agent | Severity |
|---|-------|-------|----------|
| 1 | scenario.started | ORCH-001 | INFO |
| 2 | detection.suitability_violation | CS-001 | HIGH |
| 3 | consensus.reached | ORCH-001 | INFO |
| 4 | escalation.created (Tier 4) | ORCH-001 | ALERT |
| 5 | report.generated (×5) | RG-001 | INFO |
| 6 | scenario.completed | ORCH-001 | INFO |
