# CS-09: Sanctions Violation — Indirect Counterparty Exposure

**Scenario ID:** CS-09
**Agents Required:** TM + RU
**Complexity:** High
**Expected Alert:** CRITICAL
**Applicable Regulations:** OFAC Regulations, 31 CFR Part 501, EU Sanctions Regulation

---

## 1. Scenario Description

A corporate client's wire transfer is routed through three intermediary banks to a final beneficiary that is a subsidiary of an OFAC SDN list entity, added 48 hours ago.

---

## 2. Signal Detection

### 2.1 Transaction Monitor (TM-001)

**Initial Detection:** Wire transfer to high-risk beneficiary through intermediary chain

The TM detects the wire transfer but requires sanctions screening integration for full detection. In the current implementation, the TM signals the transaction pattern but the sanctions match requires RU coordination.

**Confidence:** 0.70 (partial — awaiting sanctions screening)

### 2.2 Regulatory Update Tracker (RU-001)

**Detection:** SDN list update — beneficiary entity now sanctioned

**Confidence:** 0.85

```json
{
  "violation_type": "SANCTIONS_VIOLATION",
  "severity": "CRITICAL",
  "confidence": 0.85,
  "description": "Potential sanctions violation: wire transfer to SDN-listed subsidiary, entity added 48 hours ago",
  "evidence": [
    {"source": "sanctions_screening", "description": "Beneficiary matches SDN list entity"},
    {"source": "wire_transfer_log", "description": "3 intermediary banks in transfer chain"}
  ],
  "regulations": ["OFAC Regulations", "31 CFR Part 501", "EU Sanctions Regulation"],
  "jurisdictions": ["US", "EU"],
  "requires_sar": true
}
```

---

## 3. Consensus

```json
{
  "TM-001": {"detected": true, "confidence": 0.70, "severity": "HIGH"},
  "CS-001": {"detected": false, "confidence": 0.30, "severity": "LOW"},
  "RU-001": {"detected": true, "confidence": 0.85, "severity": "CRITICAL"}
}
```

**Bayesian:** Posterior = 0.9314 (two agents detect)
**DS Belief:** 0.9369
**Combined:** 0.9086 → DETECT

**Escalation:** CRITICAL → Tier 3 (Manager) — immediate transaction hold recommended

---

## 4. Note on Current Implementation

The sanctions screening is context-driven in the test data. TM-001 flags the high-risk wire transfer (HIGH, confidence 0.70) and RU-001 confirms the SDN match from the regulatory feed (CRITICAL, confidence 0.85). A production system would integrate with the OFAC SDN API for real-time screening. The current implementation demonstrates the multi-agent coordination pattern for cross-referencing transaction data with regulatory updates.

---

## 5. Audit Trail
| # | Event | Agent | Severity |
|---|-------|-------|----------|
| 1 | scenario.started | ORCH-001 | INFO |
| 2 | detection.sanctions_violation | TM-001 | HIGH |
| 3 | detection.sanctions_violation | RU-001 | CRITICAL |
| 4 | consensus.reached | ORCH-001 | INFO |
| 5 | escalation.created (Tier 3) | ORCH-001 | ALERT |
| 6 | report.generated (×5) | RG-001 | INFO |
| 7 | scenario.completed | ORCH-001 | INFO |
