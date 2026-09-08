# CS-13: Off-Channel Communication — Personal Device Usage

**Scenario ID:** CS-13
**Agents Required:** CS
**Complexity:** Medium
**Expected Alert:** HIGH
**Applicable Regulations:** SEC Rule 17a-4, FINRA Rule 3110

---

## 1. Scenario Description

Surveillance systems detect 7 registered representatives conducting business via personal WhatsApp accounts, including trade confirmations, investment recommendations, and client account discussions not captured in firm recordkeeping systems.

---

## 2. Signal Detection

### 2.1 Communication Scanner (CS-001)

**Detection:** Off-channel business communications

**Analysis:**
- 7 representatives using personal WhatsApp for business
- Communications include: trade confirmations, investment recommendations, client discussions
- None captured in firm recordkeeping systems

**Confidence:** 0.82

```json
{
  "violation_type": "OFF_CHANNEL_COMMS",
  "severity": "HIGH",
  "confidence": 0.82,
  "description": "Off-channel communication: 7 reps using personal WhatsApp for business, not in recordkeeping",
  "evidence": [
    {"source": "channel_surveillance", "description": "Business communications via unauthorized WhatsApp accounts"}
  ],
  "regulations": ["SEC Rule 17a-4", "FINRA Rule 3110"],
  "jurisdictions": ["US"]
}
```

---

## 3. Consensus

```json
{
  "TM-001": {"detected": false, "confidence": 0.30, "severity": "LOW"},
  "CS-001": {"detected": true, "confidence": 0.82, "severity": "HIGH"},
  "RU-001": {"detected": false, "confidence": 0.30, "severity": "LOW"}
}
```

**Combined:** 0.5355 → DETECT (via any_agent_detected)
**Escalation:** HIGH → Tier 2 (Senior Analyst)

**Context from JPMorgan Case Study (Case Study 1):**
This scenario mirrors the JPMorgan $200M fine for off-channel communications. The system should detect:
- Absence of official channel communications from active traders (negative signal)
- Metadata analysis showing low official channel volume vs trading activity
- Pattern across an entire department (systemic, not isolated)

---

## 4. Audit Trail
| # | Event | Agent | Severity |
|---|-------|-------|----------|
| 1 | scenario.started | ORCH-001 | INFO |
| 2 | detection.off_channel_comms | CS-001 | HIGH |
| 3 | consensus.reached | ORCH-001 | INFO |
| 4 | escalation.created (Tier 2) | ORCH-001 | ALERT |
| 5 | report.generated (×5) | RG-001 | INFO |
| 6 | scenario.completed | ORCH-001 | INFO |
