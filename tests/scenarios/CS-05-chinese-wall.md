# CS-05: Chinese Wall Breach — Information Leakage

**Scenario ID:** CS-05
**Agents Required:** CS
**Complexity:** High
**Expected Alert:** CRITICAL
**Applicable Regulations:** SEC Section 15(g), FINRA Rule 5280, MiFID II Article 33

---

## 1. Scenario Description

An investment banker working on a confidential M&A deal messages a friend in equity research: 'Don't cover TechCorp next week, trust me.' The research department subsequently delays publication of a TechCorp research report.

---

## 2. Signal Detection

### 2.1 Communication Scanner (CS-001)

**Detection 1: Chinese Wall Breach**
- Cross-department communication (IB → Research)
- Contains barrier breach indicators: "Don't cover", "trust me"
- Research department delayed TechCorp report after receiving message

**Confidence:** 0.80

```json
{
  "violation_type": "CHINESE_WALL_BREACH",
  "severity": "CRITICAL",
  "confidence": 0.80,
  "description": "Information barrier breach: IB communicated deal-sensitive information to equity research, causing research delay",
  "evidence": [
    {"source": "cross_department_scan", "description": "Message from IB to Research with barrier indicators"},
    {"source": "research_audit", "description": "TechCorp report delayed after IB-Research communication"}
  ],
  "regulations": ["SEC Section 15(g)", "FINRA Rule 5280", "MiFID II Article 33"],
  "jurisdictions": ["US", "EU"]
}
```

---

## 3. Consensus

```json
{
  "TM-001": {"detected": false, "confidence": 0.30, "severity": "LOW"},
  "CS-001": {"detected": true, "confidence": 0.80, "severity": "CRITICAL"},
  "RU-001": {"detected": false, "confidence": 0.30, "severity": "LOW"}
}
```

**Combined:** 0.5355 → DETECT (via any_agent_detected trigger)
**Escalation:** CRITICAL + cross-jurisdictional → Tier 4 (Director/CCO)

**Decision Support:**
```
Information barrier breach between Investment Banking and Equity Research
CRITICAL: M&A deal information leaked, research publication delayed
Regulations: SEC §15(g), FINRA Rule 5280, MiFID II Art. 33
Actions: Preserve all communications, investigate IB-Research contacts, notify Legal
```

---

## 4. Audit Trail
| # | Event | Agent | Severity |
|---|-------|-------|----------|
| 1 | scenario.started | ORCH-001 | INFO |
| 2 | detection.chinese_wall_breach | CS-001 | CRITICAL |
| 3 | consensus.reached | ORCH-001 | INFO |
| 4 | escalation.created (Tier 4) | ORCH-001 | ALERT |
| 5 | report.generated (×5) | RG-001 | INFO |
| 6 | scenario.completed | ORCH-001 | INFO |
