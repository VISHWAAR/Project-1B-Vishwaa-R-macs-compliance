# CS-18: FALSE POSITIVE — Legitimate Block Trade

**Scenario ID:** CS-18
**Agents Required:** TM
**Complexity:** Medium
**Expected Alert:** NO ALERT
**THIS IS A CRITICAL TEST:** Incorrectly escalating this scenario incurs a -25 point deduction.

---

## 1. Scenario Description

A large institutional client executes a $450 million block trade in a single equity (8% of ADV). The trade was pre-arranged with the block desk, has proper documentation, and is part of a disclosed portfolio rebalancing programme.

---

## 2. Signal Detection

### 2.1 Transaction Monitor (TM-001)

**Initial Detection Signal:** Large trade exceeding normal thresholds

**Analysis:**
- Trade amount: $450M (8% of ADV — unusually large)
- Without context, this would trigger concentration/manipulation alert
- Single equity, single day

**BUT — False Positive Verification:**

The TM checks verification data provided in the scenario context:
```json
{
  "is_legitimate": true,
  "reason": "Pre-arranged block trade with proper documentation, part of disclosed portfolio rebalancing programme"
}
```

**TM.check_false_positive()** is called:
```python
if verification_data.get("is_legitimate", False):
    return {
        **detection,
        "is_false_positive": True,
        "severity": "NO_ALERT",
        "confidence": 0.0,
        "fp_reason": "Verified legitimate activity"
    }
```

**Result:** Detection is SUPPRESSED. No alert generated.

### 2.2 Communication Scanner (CS-001)

**No communications flagged** — this is a legitimate institutional trade.

### 2.3 Regulatory Update Tracker (RU-001)

**No regulatory updates** relevant to this scenario.

---

## 3. Inter-Agent Communication

### 3.1 TM → ORCH: No ALERT

The TM detects the large trade but verifies it as a false positive. No ALERT message is sent to the orchestrator.

The only message is a HEARTBEAT confirming the agent is operational.

---

## 4. Consensus Resolution

### 4.1 Agent Assessments

```json
{
  "TM-001": {"detected": false, "confidence": 0.30, "severity": "LOW"},
  "CS-001": {"detected": false, "confidence": 0.30, "severity": "LOW"},
  "RU-001": {"detected": false, "confidence": 0.30, "severity": "LOW"}
}
```

### 4.2 Consensus

```
Bayesian Posterior: ~0.05 (very low — no agents detect)
DS Belief Violation: ~0.03
Combined: 0.03
Decision: NO_DETECT
Conflict Level: low (all agents agree: no violation)
```

---

## 5. Escalation Decision

**No escalation.** The consensus is NO_DETECT with no agent detecting a violation.

---

## 6. Report Generation

Reports are generated with "No violations detected" status for all 5 audiences.

---

## 7. Audit Trail

| # | Event | Agent | Severity |
|---|-------|-------|----------|
| 1 | scenario.started | ORCH-001 | INFO |
| 2 | scenario.completed | ORCH-001 | INFO |

**Minimal audit trail** — no detection events, no escalation events.

---

## 8. Why This Matters

CS-18 tests the system's ability to **suppress false positives**. In production:
- False positive rates above 5% cause "alert fatigue" in compliance teams
- Legitimate block trades happen daily at large institutions
- The system must distinguish between:
  - Genuine suspicious activity (requires escalation)
  - Normal but large transactions (requires context-aware suppression)

The key mechanism: the False Positive Slayer badge is earned by correctly handling this scenario with documented reasoning.

---

## 9. System Verification

```
CS-18: FALSE POSITIVE
  Detections: 0
  Consensus: no_detect (confidence: 0.03)
  Escalation: None
  ✅ CS-18 CORRECTLY: No escalation
```
