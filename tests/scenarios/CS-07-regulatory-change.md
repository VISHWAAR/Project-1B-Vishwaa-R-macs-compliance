# CS-07: Regulatory Change Impact — New Margin Requirements

**Scenario ID:** CS-07
**Agents Required:** RU
**Complexity:** Medium
**Expected Alert:** MEDIUM
**Applicable Regulations:** SEC Swap Margin Rule, Basel III CRE54, EMIR Margin RTS

---

## 1. Scenario Description

The SEC publishes a final rule increasing initial margin for uncleared swaps by 25%, effective in 120 days, with new variation margin methodologies differing from Basel III standards.

---

## 2. Signal Detection

### 2.1 Regulatory Update Tracker (RU-001)

**Detection:** Regulatory change requiring impact assessment

**Analysis:**
- New SEC rule: +25% initial margin for uncleared swaps
- Effective in 120 days (implementation deadline)
- New variation margin methodologies differ from Basel III
- Impact on existing compliance framework: significant

**Confidence:** 0.75

```json
{
  "violation_type": "REGULATORY_CHANGE",
  "severity": "MEDIUM",
  "confidence": 0.75,
  "description": "Regulatory change requiring impact assessment: SEC +25% margin for uncleared swaps, 120-day deadline",
  "evidence": [
    {"source": "regulatory_feed", "description": "SEC Final Rule: Increased Initial Margin for Uncleared Swaps"}
  ],
  "regulations": ["SEC Swap Margin Rule", "Basel III CRE54", "EMIR Margin RTS"],
  "jurisdictions": ["US", "EU"]
}
```

---

## 3. Consensus

```json
{
  "TM-001": {"detected": false, "confidence": 0.30, "severity": "LOW"},
  "CS-001": {"detected": false, "confidence": 0.30, "severity": "LOW"},
  "RU-001": {"detected": true, "confidence": 0.75, "severity": "MEDIUM"}
}
```

**Combined:** 0.5946 → DETECT
**Escalation:** MEDIUM severity → Tier 2 (Senior Analyst)

**Impact Assessment:**
- Affected agents: All (TM thresholds, RG templates, CS rules)
- Estimated implementation: 30 days
- Actions: Update margin calculation models, revise reporting templates, train staff

---

## 4. Audit Trail
| # | Event | Agent | Severity |
|---|-------|-------|----------|
| 1 | scenario.started | ORCH-001 | INFO |
| 2 | detection.regulatory_change | RU-001 | MEDIUM |
| 3 | consensus.reached | ORCH-001 | INFO |
| 4 | escalation.created (Tier 2) | ORCH-001 | ALERT |
| 5 | report.generated (×5) | RG-001 | INFO |
| 6 | scenario.completed | ORCH-001 | INFO |
