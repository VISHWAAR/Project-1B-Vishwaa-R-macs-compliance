# Communication Scanner Agent (CS-001)

## Overview

The Communication Scanner monitors all business communications for compliance violations across multiple channels and languages. It detects misleading statements, coercive language, information barrier (Chinese wall) breaches, off-channel communications, elder exploitation indicators, and information leakage.

**Agent ID:** CS-001  
**Module:** `agents/communication_scanner.py`  
**Class:** `CommunicationScanner`

## Detection Pipeline

The agent runs 6 independent detection pipelines on each communication batch:

```
scan_communications(communications, scenario_id, context)
│
├─ _detect_misleading_statements()       → MISLEADING_STATEMENTS
├─ _detect_chinese_wall_breach()        → CHINESE_WALL_BREACH
├─ _detect_off_channel_comms()          → OFF_CHANNEL_COMMS
├─ _detect_coercive_language()          → MISLEADING_STATEMENTS (coercive subtype)
├─ _detect_elder_exploitation_comms()   → ELDER_EXPLOITATION
└─ _detect_information_leakage()        → CHINESE_WALL_BREACH (leakage subtype)
```

## Detection Lexicons

### Misleading Statement Keywords

```
"guaranteed", "guarantee", "zero risk", "no risk", "risk-free",
"can't lose", "cannot lose", "sure thing", "100% safe",
"no chance of loss", "certain return", "assured returns",
"double your money", "get rich", "once in a lifetime"
```

### Coercive Language Keywords

```
"you must", "you have to", "no choice", "act now or lose",
"last chance", "don't miss out", "limited time only",
"if you don't", "you'll regret", "you'd be foolish",
"everyone else is", "fear of missing out", "pressure"
```

### Chinese Wall Breach Keywords

```
"don't cover", "delay publication", "hold the report",
"trust me", "off the record", "confidential deal",
"m&a target", "acquisition target", "merger pending",
"keep this between", "not public yet"
```

### Off-Channel Communication Indicators

```
"whatsapp", "signal", "telegram", "personal email",
"text me", "call me on my personal", "not on the system",
"delete this message", "ephemeral", "disappearing"
```

### Elder Exploitation Indicators

```
"power of attorney", "poa", "new beneficiary",
"unsolicited trade", "unusual activity", "elderly",
"vulnerable adult", "trusted contact"
```

## Context-Based Detection

The CS agent also supports context-driven detection for scenarios where the test harness provides pre-computed signals:

| Context Flag | Detection Triggered | Severity |
|-------------|--------------------|----------|
| `misleading_statements_detected` | MISLEADING_STATEMENTS | CRITICAL (if many clients affected) / HIGH |
| `chinese_wall_breach` | CHINESE_WALL_BREACH | CRITICAL |
| `off_channel_detected` | OFF_CHANNEL_COMMS | HIGH |
| `elder_exploitation_signals` | ELDER_EXPLOITATION | CRITICAL |
| `info_leakage_detected` | CHINESE_WALL_BREACH | CRITICAL |

Context-based detection takes priority over keyword scanning and uses the `cs_confidence` value from context (default 0.7-0.75).

## Confidence Calculation

Keyword-based confidence grows with the number of matched keywords:

```python
# Misleading statements: 0.4 base + 0.1 per keyword, cap 0.9
confidence = min(0.9, 0.4 + 0.1 * len(found_keywords))

# Coercive language: 0.4 base + 0.1 per keyword, cap 0.85
confidence = min(0.85, 0.4 + 0.1 * len(found_keywords))

# Chinese wall (cross-dept): 0.5 base + 0.1 per keyword, cap 0.9
confidence = min(0.9, 0.5 + 0.1 * len(found))

# Off-channel: 0.4 base + 0.15 per keyword, cap 0.85
confidence = min(0.85, 0.4 + 0.15 * len(found))
```

## Violation Types Detected

- `MISLEADING_STATEMENTS` — False performance claims, guaranteed returns, risk-free assertions
- `CHINESE_WALL_BREACH` — Cross-department information leakage, M&A deal details shared
- `OFF_CHANNEL_COMMS` — Business conducted via unauthorized channels (WhatsApp, Signal, personal email)
- `ELDER_EXPLOITATION` — Suspicious activity involving elderly/vulnerable clients

## Multi-Language Support

The current implementation focuses on English-language keyword detection. The architecture supports multi-language extension through additional lexicon files. The design document specifies support for English, Mandarin, Hindi, and Spanish.

## Privacy Constraints

1. **No decryption of E2E-encrypted communications** — voice analysis limited to transcribed text
2. **Respect data retention boundaries** — communications processed inline, not stored
3. **Cannot independently determine legal privilege** — privilege detection flags for human review only
4. **Privacy-preserving analysis** — personal communications scanned for compliance keywords without content retention

## Resource Requirements

| Resource | Value |
|----------|-------|
| CPU Cores | 4.0 |
| Memory | 2048 MB |
| Max Concurrent Tasks | 20 |
| SLA Throughput | 500 events/sec |
| SLA Max Latency | 2000 ms |
| SLA Availability | 99.9% |

## Dependencies

- RU-001: Regulatory Update Tracker (provides regulatory context for detection thresholds)

## Implementation

See `agents/communication_scanner.py` — `CommunicationScanner` class, all `_detect_*` methods, lexicon constants (MISLEADING_KEYWORDS, COERCIVE_KEYWORDS, etc.).
