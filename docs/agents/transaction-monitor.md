# Transaction Monitor Agent (TM-001)

## Overview

The Transaction Monitor is the primary detection agent for trading and financial transaction violations. It continuously surveils transaction activity across all monitored venues and products, applying statistical pattern detection, threshold monitoring, temporal analysis, counterparty analysis, and cross-market surveillance.

**Agent ID:** TM-001  
**Module:** `agents/transaction_monitor.py`  
**Class:** `TransactionMonitor`

## Detection Pipeline

The agent runs 9 independent detection pipelines in sequence on each transaction batch:

```
analyze_transaction_batch(transactions, context)
│
├─ _detect_insider_trading()        → INSIDER_TRADING
├─ _detect_spoofing()              → SPOOFING_LAYERING
├─ _detect_aml_structuring()       → AML_STRUCTURING
├─ _detect_wash_trading()          → WASH_TRADING
├─ _detect_concentration_risk()    → CONCENTRATION_RISK
├─ _detect_sanctions()             → SANCTIONS_VIOLATION
├─ _detect_front_running()         → FRONT_RUNNING
├─ _detect_late_trading()          → LATE_TRADING
└─ _detect_best_execution()        → BEST_EXECUTION_FAILURE
```

Each pipeline checks scenario context flags (e.g., `context.get("tm_signals")`, `context.get("spoofing_signals")`) before running, so agents only consume compute for relevant scenarios.

## Detection Rules Summary

| Violation Type | Key Rule Parameters | Confidence Calculation |
|---------------|--------------------|----------------------|
| Insider Trading | 21-day accumulation window, 20% price increase threshold, 30-day communication link window | Base confidence from context + 0.15 bonus if communication link confirmed by CS |
| Spoofing/Layering | 85% cancel rate threshold, 500ms max order lifetime, min 5 spoof orders, 70% opposite-side execution ratio | 0.3 per criterion met, capped at 0.95 |
| AML Structuring | $10K reporting threshold, $8K-$9,999 structuring range, min 3 deposits, 10-day window, 3+ branches | 0.3 per criterion, capped at 0.95 |
| Wash Trading | Min 5 matching trades, 5 bps price tolerance, 14-day window, 80% volume threshold | 0.4 + 0.3 + 0.3 by criterion, capped at 0.95 |
| Concentration Risk | 25% sector limit, 3-day persistence, 10pt material exceedance | 0.5 + 0.04 × exceedance + 0.02 × days, capped at 0.95 |
| Sanctions | SDN screening confidence 0.70 (partial — requires RU confirmation), max 1 intermediary bank | Fixed 0.70 by design (partial detection) |
| Front-Running | 30 min before client order, 80% profit rate, min 20 trades, 70% correlation | 0.4 + 0.3 + 0.3 by criterion, capped at 0.95 |
| Late Trading | Post-cutoff mutual fund orders | 0.5 + 0.05 × late_orders, capped at 0.95 |
| Best Execution | 70% single-venue routing, >1 better-priced venue, >0.5¢/share improvement | 0.4 + 0.3 + 0.3 by criterion, capped at 0.95 |

## Violation Types Detected

- `INSIDER_TRADING` — Pre-announcement accumulation with price spike
- `SPOOFING_LAYERING` — Large order cancellation patterns
- `AML_STRUCTURING` — Cash deposits just below $10K reporting threshold
- `WASH_TRADING` — Matching trades between controlled accounts
- `CONCENTRATION_RISK` — Sector exposure exceeding limits
- `SANCTIONS_VIOLATION` — Wire transfers to SDN-listed entities
- `FRONT_RUNNING` — Personal trades ahead of client orders
- `LATE_TRADING` — Mutual fund orders after NAV cutoff
- `BEST_EXECUTION_FAILURE` — Systematic routing to single venue

## False Positive Handling

The `check_false_positive()` method handles CS-18 (legitimate block trade that would otherwise trigger an alert):

```python
def check_false_positive(self, detection, verification_data):
    if verification_data.get("is_legitimate", False):
        return {
            **detection,
            "is_false_positive": True,
            "severity": "NO_ALERT",
            "confidence": 0.0,
            "fp_reason": verification_data.get("reason", "..."),
        }
    return detection
```

The orchestrator's `_node_run_agents` applies this check when `context.get("is_false_positive")` is True, then removes any detections that became NO_ALERT.

## Resource Requirements

| Resource | Value |
|----------|-------|
| CPU Cores | 4.0 |
| Memory | 2048 MB |
| Max Concurrent Tasks | 20 |
| SLA Throughput | 1000 events/sec |
| SLA Max Latency | 500 ms |
| SLA Availability | 99.95% |

## Constraints

- Cannot access raw customer communications (must rely on CS-001 for communication context)
- Detection confidence scores must be calibrated against historical false positive rates (baseline FP rate: 5%)
- Cannot issue trading halts autonomously
- Must maintain sub-second latency for real-time monitoring
- Sanctions detection is partial (0.70 confidence) — requires RU-001 coordination for full SDN confirmation

## Dependencies

- CS-001: Communication Scanner (provides communication link evidence for insider trading cases)

## Implementation

See `agents/transaction_monitor.py` — `TransactionMonitor` class, all `_detect_*` methods, `check_false_positive()`.
