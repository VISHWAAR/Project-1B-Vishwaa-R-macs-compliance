# CS-20: Coordinated AML — Complex Money Laundering through Trade Finance

**Scenario ID:** CS-20
**Agents Required:** ALL FOUR (TM + CS + RU + RG)
**Complexity:** Very High
**Expected Alert:** CRITICAL
**Trace-Through Length:** 5-8 pages (this is the most complex scenario)

---

## 1. Scenario Description

A trade finance client submits letters of credit for goods priced 300% above market value. The beneficiary is in a high-risk jurisdiction. Internal communications show a relationship manager overrode compliance screening flags twice. Wire transfers are routed through 5 intermediary banks. A regulatory update 2 weeks ago added the beneficiary's country to an enhanced due diligence list.

This scenario tests **full system coordination** across all four agents.

---

## 2. Signal Detection (All Agents)

### 2.1 Transaction Monitor (TM-001)

**Detection 1: Trade-Based Money Laundering**
- Letters of credit for goods priced 300% above market value
- Beneficiary in high-risk jurisdiction
- Wire transfers routed through 5 intermediary banks (layering pattern)

**Confidence:** 0.85

```json
{
  "violation_type": "AML_STRUCTURING",
  "severity": "CRITICAL",
  "confidence": 0.85,
  "description": "Suspected trade-based money laundering: LCs for goods at 300% market value, "
                "beneficiary in high-risk jurisdiction, 5 intermediary banks",
  "evidence": [
    {"source": "trade_finance_system", "description": "LC pricing 300% above market"},
    {"source": "wire_transfer_log", "description": "5 intermediary banks in transfer chain"},
    {"source": "sanctions_screening", "description": "Beneficiary jurisdiction on enhanced due diligence list"}
  ]
}
```

**Detection 2: Compliance Override Pattern**
- RM overrode compliance screening flags twice
- Unusual override pattern for this relationship manager

**Confidence:** 0.80

### 2.2 Communication Scanner (CS-001)

**Detection: Compliance Override Communications**
- Internal messages showing RM instructed compliance override
- Text: "Override compliance screening for this client, they are a priority relationship"

**Confidence:** 0.82

```json
{
  "violation_type": "CHINESE_WALL_BREACH",
  "severity": "CRITICAL",
  "confidence": 0.82,
  "description": "Relationship manager overrode compliance screening flags twice, "
                "indicating potential compliance function suppression",
  "evidence": [
    {"source": "internal_messages", "description": "RM instructed compliance override"},
    {"source": "compliance_audit_log", "description": "Two screening overrides by same RM"}
  ]
}
```

### 2.3 Regulatory Update Tracker (RU-001)

**Detection: Regulatory Change Impact**
- Beneficiary's country added to enhanced due diligence list 2 weeks ago
- Current transactions may violate updated requirements

**Confidence:** 0.75

```json
{
  "violation_type": "REGULATORY_CHANGE",
  "severity": "HIGH",
  "confidence": 0.75,
  "description": "Beneficiary country added to FATF enhanced due diligence list 2 weeks ago. "
                "Current LC transactions may violate updated screening requirements.",
  "evidence": [
    {"source": "regulatory_feed", "description": "FATF updated watchlist"},
    {"source": "screening_system", "description": "Transactions processed before screening update"}
  ]
}
```

### 2.4 Report Generator (RG-001)

The RG doesn't detect violations but prepares the comprehensive report incorporating all agent findings.

---

## 3. Inter-Agent Communication Flow

```
                    ┌─────────────┐
    TM ─── ALERT ──→│             │
                    │  ORCHESTRATOR│
    CS ─── ALERT ──→│  (ORCH-001) │
                    │             │
    RU ─── UPDATE ─→│             │
                    └──────┬──────┘
                           │
                    ┌──────▼──────┐
                    │  CONSENSUS  │
                    │   ENGINE    │
                    └──────┬──────┘
                           │
                    ┌──────▼──────┐
                    │  ESCALATION │
                    │  (Tier 4)   │
                    └──────┬──────┘
                           │
                    ┌──────▼──────┐
                    │   REPORT    │
                    │  GENERATOR  │
                    └─────────────┘
```

### 3.1 Message Timeline

| # | From | To | Type | Priority | Content |
|---|------|-----|------|----------|---------|
| 1 | TM-001 | ORCH-001 | ALERT | CRITICAL | Trade-based ML detection |
| 2 | CS-001 | ORCH-001 | ALERT | CRITICAL | RM compliance override |
| 3 | RU-001 | ORCH-001 | UPDATE | HIGH | Enhanced due diligence update |
| 4 | ORCH-001 | ALL | QUERY | HIGH | Request additional evidence |
| 5 | TM-001 | ORCH-001 | RESPONSE | HIGH | Wire transfer chain details |
| 6 | CS-001 | ORCH-001 | RESPONSE | HIGH | Communication evidence |
| 7 | RU-001 | ORCH-001 | RESPONSE | HIGH | Regulatory impact assessment |
| 8 | ORCH-001 | ORCH-001 | INTERNAL | — | Consensus computation |
| 9 | ORCH-001 | HUMAN | ESCALATION | CRITICAL | Tier 4 escalation |

---

## 4. Consensus Resolution

### 4.1 Agent Assessments

```json
{
  "TM-001": {"detected": true, "confidence": 0.85, "severity": "CRITICAL",
             "violation_type": "AML_STRUCTURING"},
  "CS-001": {"detected": true, "confidence": 0.82, "severity": "CRITICAL",
             "violation_type": "CHINESE_WALL_BREACH"},
  "RU-001": {"detected": true, "confidence": 0.75, "severity": "HIGH",
             "violation_type": "REGULATORY_CHANGE"}
}
```

### 4.2 Conflict Detection

**Type A (Severity Disagreement):** TM and CS say CRITICAL, RU says HIGH
→ Resolution: Highest authority (TM) → CRITICAL

**No Existence Disagreement:** All 3 agents detect violations ✓

### 4.3 Bayesian Consensus

```
Prior: P(H) = 0.3

TM evidence (detected, 0.85):
  LR = 1 + 0.85 × 9 = 8.65
  P(H|TM) = 0.7874

CS evidence (detected, 0.82):
  LR = 1 + 0.82 × 9 = 8.38
  P(H|TM,CS) = 0.9759

RU evidence (detected, 0.75):
  LR = 1 + 0.75 × 9 = 7.75
  P(H|TM,CS,RU) = 0.9968

Bayesian Posterior: 0.9968
```

### 4.4 Dempster-Shafer

```
Combined DS Belief Violation: 0.9987
Uncertainty: 0.0013
Conflict Level: low
```

### 4.5 Final Consensus

```
Combined = 0.4 × 0.9968 + 0.3 × 0.9987 + 0.3 × 0.85 = 0.9563
Decision: DETECT
Confidence: 0.9563 (highest of all scenarios)
Conflict Level: low
```

---

## 5. Escalation Decision

### 5.1 Triggers Activated
- ✅ HIGH_CONFIDENCE_DETECTION (0.85 > 0.8)
- ✅ CRITICAL_SEVERITY
- ✅ CROSS_JURISDICTIONAL (US, EU, Singapore)

### 5.2 Tier Assignment
CRITICAL severity + cross-jurisdictional → **Tier 4 (Director/CCO)**

### 5.3 Decision Support Package

```
MULTI-DIMENSIONAL COMPLIANCE VIOLATION

Detection Summary:
- Trade-based money laundering via inflated LC pricing (TM)
- Compliance function suppression by RM (CS)
- Regulatory screening gap due to recent FATF update (RU)

Severity: CRITICAL
Confidence: 95.6%
Agents Reporting: 3/3 (all detect)
Conflicts: 1 (severity only, resolved)

Evidence Package:
1. LC pricing 300% above market value
2. 5-bank wire transfer chain (layering)
3. RM compliance override messages
4. FATF watchlist update (2 weeks ago)

Applicable Regulations:
- BSA/AML (Bank Secrecy Act)
- OFAC (Office of Foreign Assets Control)
- Trade-Based Money Laundering Red Flags
- FATF Recommendations

Recommended Actions:
1. IMMEDIATE: Freeze all pending LC transactions
2. FILE: Suspicious Activity Report (SAR) within 24 hours
3. INVESTIGATE: RM conduct and override history
4. NOTIFY: Board Risk Committee and Legal
5. SCREEN: All transactions against updated FATF list
6. PRESERVE: All communications and transaction records

SLA: 24 hours for Tier 4 initial response
```

---

## 6. Report Generation

### 6.1 Multi-Audience Reports (5 generated)

| Audience | Focus | Detail Level |
|----------|-------|-------------|
| Operations | Detection details, investigation steps | Detailed |
| Management | Financial impact, regulatory risk | Moderate |
| Board | Strategic implications, reputation risk | High-level |
| Regulator | Regulatory citations, evidence package | Comprehensive |
| Auditor | Control effectiveness, audit trail | Comprehensive |

### 6.2 SAR Draft Prepared

The RG prepares a Suspicious Activity Report draft:
- Document type: SAR_DRAFT
- Status: pending_dual_sign_off
- Filing deadline: 30 days
- Sign-off required: Compliance Officer + MLRO

---

## 7. Audit Trail

| # | Event | Agent | Severity | Trace |
|---|-------|-------|----------|-------|
| 1 | scenario.started | ORCH-001 | INFO | trace-CS-20-001 |
| 2 | detection.aml_structuring | TM-001 | CRITICAL | trace-CS-20-001 |
| 3 | detection.chinese_wall_breach | CS-001 | CRITICAL | trace-CS-20-001 |
| 4 | detection.regulatory_change | RU-001 | HIGH | trace-CS-20-001 |
| 5 | consensus.reached | ORCH-001 | INFO | trace-CS-20-001 |
| 6 | escalation.created (Tier 4) | ORCH-001 | ALERT | trace-CS-20-001 |
| 7 | report.generated (×5) | RG-001 | INFO | trace-CS-20-001 |
| 8 | scenario.completed | ORCH-001 | INFO | trace-CS-20-001 |

**Chain Integrity:** SHA-256 hash-verified, no gaps, all entries timestamped.

---

## 8. System Verification

```
CS-20: Coordinated AML
  Detections: 2 (TM + CS + RU detected different aspects)
  Consensus: detect (confidence: 0.9563)
  Escalation: Tier 4 (Director/CCO)
  Reports: 5 audiences
  Audit Trail: 8+ entries (hash-chained)
```
