# Inter-Agent Communication Protocol

**Version:** 1.0.0
**Protocol:** MACS Message Protocol v1

---

## 1. Protocol Overview

All inter-agent communication in the MACS system uses a standardized message protocol based on the specification in Appendix B. Every message between agents is wrapped in a `MessageEnvelope` conforming to the Pydantic models defined in `protocols/message_schema.py`.

## 2. Message Types

| Type | Purpose | Requires Response | Typical Sender |
|------|---------|------------------|----------------|
| ALERT | Detection event notification | No | TM, CS, RU |
| QUERY | Request for data/analysis | Yes | Any → Any |
| RESPONSE | Answer to a QUERY | No | Any |
| UPDATE | Broadcast of state changes | No | RU, ORCH |
| HEARTBEAT | Periodic health status | No | All → ORCH |
| ESCALATION | Human-in-the-loop request | Yes (human) | ORCH → Human |

## 3. Priority Levels & SLAs

| Priority | Level | SLA | Use Case |
|----------|-------|-----|----------|
| 1 | CRITICAL | 15 minutes | Active compliance violation, sanctions hit |
| 2 | HIGH | 1 hour | Confirmed violation, regulatory deadline |
| 3 | MEDIUM | 4 hours | Suspected violation, regulatory change |
| 4 | LOW | 24 hours | Informational update, threshold adjustment |
| 5 | INFORMATIONAL | Best effort | Heartbeat, diagnostic, performance metric |

## 4. Message Envelope Structure

Every message contains:
- **Identity**: message_id (UUID v4), protocol_version (semver), timestamp (ISO 8601 UTC)
- **Routing**: sender_agent_id, recipient_agent_id, message_type, priority
- **Tracing**: correlation_id (links related messages), trace_id (distributed tracing)
- **Payload**: payload_schema (identifier), payload (structured content)
- **Confidence**: confidence_score (0.0-1.0, optional)
- **Delivery**: ttl_seconds, retry_count
- **Audit**: audit_classification (REGULATORY/OPERATIONAL/DIAGNOSTIC)
- **Security**: sender_signature (cryptographic), nonce (replay prevention)

## 5. Error Handling

### 5.1 Timeout
If a message is not delivered within the priority SLA, it is retried with exponential backoff:
- Base delay: 2 seconds
- Max retries: 3
- Jitter: random 0-500ms

### 5.2 Dead Letter Queue
Messages that exhaust retries are moved to the dead letter queue (max 1000 messages) for inspection.

### 5.3 Back-Pressure
Queue depth is monitored per agent. Warning at 80% capacity, critical at 95%.

## 6. Protocol Versioning

- Protocol version uses semantic versioning (MAJOR.MINOR.PATCH)
- MAJOR: breaking changes to message schema
- MINOR: new optional fields or message types
- PATCH: documentation fixes, non-breaking changes
- Current version: 1.0.0
# Protocol update
