# Message Routing Logic

## Overview

The message routing subsystem handles all inter-agent communication in MACS. It provides priority-based queue management with SLA enforcement, retry logic with exponential backoff, a dead letter queue for failed messages, and back-pressure monitoring. The router is the central hub through which all agent-to-agent messages flow.

## Priority Taxonomy and SLA Mapping

Every message has a priority level that determines its SLA (Service Level Agreement) — the maximum time the message can sit in a queue before it must be delivered.

| Priority | Value | SLA | Use Case |
|----------|-------|-----|----------|
| CRITICAL | 1 | 15 minutes | Insider trading alerts, sanctions violations, Chinese wall breaches |
| HIGH | 2 | 1 hour | Wash trading, spoofing, AML structuring, misleading marketing |
| MEDIUM | 3 | 4 hours | Regulatory changes, concentration risk, data privacy |
| LOW | 4 | 24 hours | Scheduled reports, audit trail queries |
| INFORMATIONAL | 5 | Best effort | Heartbeats, status updates |

SLA mapping is defined in `PRIORITY_SLA_SECONDS` in `protocols/routing.py`.

## Message Lifecycle

```
┌─────────────────┐
│ Message Created │
│ (MessageEnvelope)│
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Router.route()  │
│ - Validate proto │
│ - Check TTL     │
│ - Check retries │
└────────┬────────┘
         │
    ┌────┴────┐
    │ Expired?│──Yes──► Drop (total_expired++)
    └────┬────┘
         │ No
    ┌────┴────┐
    │ Retries │──> MAX_RETRIES──► DLQ (total_failed++)
    │ > MAX?  │
    └────┬────┘
         │ No
         ▼
┌─────────────────┐
│ Deliver or      │
│ Queue per       │
│ recipient       │
└────────┬────────┘
         │
    ┌────┴────┐
    │ Handler │──Exists──► Try direct delivery
    │ exists? │          │
    └────┬────┘          │
         │ No            │
    ┌────┴────┐          │
    │ Queued  │          │
    │ (depth  │          │
    │ check)  │          │
    └─────────┘          │
         │               │
         ▼               ▼
    ┌────────┐      ┌──────────┐
    │ Queue  │      │ Delivered│
    │ (Queued│      │ (metrics │
    │Message)│      │ updated) │
    └────────┘      └──────────┘
```

## MessageRouter Architecture

### Core Components

**`MessageRouter`** (`protocols/routing.py`):

| Component | Purpose |
|-----------|---------|
| `_handlers: Dict[str, Callable]` | Registered message handlers per agent |
| `_queues: Dict[str, List[QueuedMessage]]` | Per-recipient message queues |
| `_dead_letter_queue: List[QueuedMessage]` | Messages that exhausted retries |
| `_metrics: RouteMetrics` | Delivery statistics |
| `_protocol_version: str` | Current protocol version (1.0.0) |
| `_max_queue_depth: int` | Per-queue depth limit (10000) |

### QueuedMessage

```
QueuedMessage:
  - envelope: MessageEnvelope
  - queued_at: float (Unix timestamp)
  - attempts: int (delivery attempts so far)
  - last_attempt: Optional[float]
  - delivered: bool
  - failed: bool
```

### RouteMetrics

```
RouteMetrics:
  - total_sent: int
  - total_delivered: int
  - total_failed: int
  - total_expired: int
  - avg_delivery_latency_ms: float (running average)
  - messages_by_priority: Dict[int, int]
  - messages_by_type: Dict[str, int]
```

## Retry Logic with Exponential Backoff

When a message delivery fails (either because no handler exists, or the handler throws), the message is queued. `process_queues()` retries queued messages with exponential backoff:

```python
backoff = RETRY_BACKOFF_BASE ** msg.attempts  # 2^0=1s, 2^1=2s, 2^2=4s
elapsed = time.time() - (msg.last_attempt or msg.queued_at)

if elapsed < backoff:
    # Not yet time to retry — leave in queue
    still_queued.append(msg)
else:
    msg.attempts += 1
    msg.envelope.retry_count = msg.attempts
    try:
        handler(msg.envelope)
        msg.delivered = True
    except Exception:
        if msg.attempts > MAX_RETRIES:  # MAX_RETRIES = 3
            move_to_dead_letter(envelope)
        else:
            still_queued.append(msg)
```

**Backoff schedule:**
- Attempt 1 (first retry): 1 second wait
- Attempt 2: 2 seconds
- Attempt 3: 4 seconds
- Attempt 4 (final): would go to DLQ

## Dead Letter Queue (DLQ)

Messages that exceed `MAX_RETRIES` (3) or whose queues are full are moved to the DLQ.

```
DLQ characteristics:
- Maximum size: 1000 messages
- When full: oldest message dropped (FIFO eviction)
- Contents: full MessageEnvelope for forensic inspection
- Access: get_dead_letter_queue() returns list of envelopes
- Monitoring: total_failed counter, DLQ size in metrics
```

The DLQ is the system's "canary in the coal mine" — a growing DLQ indicates systemic delivery failures.

## SLA Violation Monitoring

`check_sla_violations()` scans all queued messages and returns those whose age exceeds their priority's SLA:

```python
violations = []
for recipient_id, queue in self._queues.items():
    for msg in queue:
        if msg.delivered or msg.failed:
            continue
        sla = PRIORITY_SLA_SECONDS.get(msg.envelope.priority, 3600)
        age = now - msg.queued_at
        if age > sla:
            violations.append({
                "message_id": msg.envelope.message_id,
                "recipient": recipient_id,
                "priority": msg.envelope.priority.name,
                "age_seconds": round(age),
                "sla_seconds": sla,
                "overdue_seconds": round(age - sla),
            })
```

SLA violations are reported in the dashboard and would trigger alerts in a production deployment.

## Queue Depth Monitoring and Back-Pressure

Each queue has a maximum depth of `_max_queue_depth` (default 10000). When a queue reaches this limit:

1. New messages for that recipient are moved to the DLQ
2. A critical error is logged
3. The queue depth is reported in `get_metrics()`

Back-pressure indicates a slow or unavailable consumer. In production, this would trigger autoscaling of the affected agent.

## Protocol Versioning

The router validates `envelope.protocol_version` against the expected version (`1.0.0`). Mismatches are logged as warnings but do not block delivery — the message is still routed. This allows gradual protocol upgrades.

```
Protocol version field:
- Format: semantic versioning (MAJOR.MINOR.PATCH)
- Current: 1.0.0
- Mismatch behavior: warning log, message still processed
```

## Error Handling Summary

| Error Condition | Behavior |
|----------------|----------|
| Message expired (TTL exceeded) | Dropped, `total_expired++` |
| Retry count > MAX_RETRIES | Moved to DLQ, `total_failed++` |
| No handler registered for recipient | Message queued for later delivery |
| Handler throws exception | Message queued for retry with backoff |
| Queue full (depth ≥ max_queue_depth) | Message moved to DLQ |
| Protocol version mismatch | Warning logged, message still processed |

## Routing Pattern in MACS

In the current MACS implementation, the `MessageRouter` is available as a singleton (`get_router()`), but the orchestrator's graph-based workflow handles agent dispatch directly rather than through message routing. The router is designed for:

1. **Production inter-agent communication** — when agents run as separate services
2. **Async message delivery** — queued messages delivered when handler becomes available
3. **Cross-process communication** — messages can be serialized and sent over IPC/network

For the current single-process scenario runner, agents are called directly, but the router infrastructure is in place for production deployment.

## Implementation

See `protocols/routing.py`:
- `MessageRouter` — core router class
- `QueuedMessage` — queued message dataclass
- `RouteMetrics` — routing statistics
- `get_router()` — singleton accessor
- Constants: `PRIORITY_SLA_SECONDS`, `MAX_RETRIES`, `RETRY_BACKOFF_BASE`, `DEAD_LETTER_QUEUE_MAX`
