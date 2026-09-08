# CS-08: Client Communication Violation — Misleading Performance Claims

**Scenario ID:** CS-08
**Agents Required:** CS
**Complexity:** Low-Medium
**Expected Alert:** CRITICAL
**Applicable Regulations:** SEC Rule 206(4)-1, FINRA Rule 2210, FCA COBS 4

---

## 1. Scenario Description

Marketing materials distributed to 3,400 prospects claim 'guaranteed 12% annual returns' and 'zero risk of capital loss' for a structured product with actual 40% capital loss potential in stress scenarios.

---

## 2. Signal Detection

### 2.1 Communication Scanner (CS-0001)

**Detection:** Misleading marketing materials with false performance claims

**Keyword Analysis:**
- "guaranteed 12% annual returns" → matches MISLEADING_KEYWORDS: "guaranteed"
- "zero risk of capital loss" → matches: "zero risk", "no risk"
- Client-facing materials distributed to 3,400 prospects

**Confidence:** 0.90

```json
{
  "violation_type": "MISLEADING_STATEMENTS",
  "severity": "CRITICAL",
  "confidence": 0.90,
  "description": "Misleading marketing: 'guaranteed 12% returns' and 'zero risk' for product with 40% loss potential, distributed to 3,400 prospects",
  "evidence": [
    {"source": "keyword_scan", "description": "Misleading claims found in marketing materials"},
    {"source": "product_analysis", "description": "Structured product has 40% capital loss potential in stress scenarios"}
  ],
  "regulations": ["SEC Rule 206(4)-1", "FINRA Rule 2210", "FCA COBS 4"],
  "jurisdictions": ["US", "UK"]
}
```

**Additional keyword detections from 3,400 communications:**
Each prospect email triggers a keyword match detection (3,400 individual detections), consolidated by the orchestrator.

---

## 3. Consensus

```json
{
  "TM-001": {"detected": false, "confidence": 0.30, "severity": "LOW"},
  "CS-001": {"detected": true, "confidence": 0.90, "severity": "CRITICAL"},
  "RU-001": {"detected": false, "confidence": 0.30, "severity": "LOW"}
}
```

**Combined:** 0.5355 → DETECT
**Escalation:** CRITICAL + cross-jurisdictional (US + UK) → Tier 4 (Director/CCO)

---

## 4. Report

RG generates regulatory filing draft for SEC and FCA:
- Marketing materials contain material misrepresentations
- 3,400 prospects potentially affected
- Product risk profile fundamentally misrepresented
- Immediate retraction of marketing materials recommended

---

## 5. Audit Trail
| # | Event | Agent | Severity |
|---|-------|-------|----------|
| 1 | scenario.started | ORCH-001 | INFO |
| 2 | detection.misleading_statements | CS-001 | CRITICAL |
| 3 | consensus.reached | ORCH-001 | INFO |
| 4 | escalation.created (Tier 4) | ORCH-001 | ALERT |
| 5 | report.generated (×5) | RG-001 | INFO |
| 6 | scenario.completed | ORCH-001 | INFO |
