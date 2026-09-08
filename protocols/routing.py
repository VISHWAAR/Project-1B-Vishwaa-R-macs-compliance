"""
Message Routing Logic

Handles message routing, priority classification, error handling,
and protocol versioning for the inter-agent communication system.

Priority SLAs:
  CRITICAL (1): 15 minutes
  HIGH (2):     1 hour
  MEDIUM (3):   4 hours
  LOW (4):      24 hours
  INFORMATIONAL (5): best effort

Error Handling:
  - Timeout: message not delivered within SLA → retry with backoff
  - Dead Letter Queue: messages that exhaust retries
  - Back-pressure: queue depth monitoring with alerting
"""

import logging
import time
from collections import defaultdict
from datetime import datetime, timezone, timedelta
from typing import Any, Callable, Dict, List, Optional
from dataclasses import dataclass, field

from protocols.message_schema import (
    MessageEnvelope, MessageType, Priority, AgentID,
)

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Priority → SLA mapping
# ---------------------------------------------------------------------------

PRIORITY_SLA_SECONDS: Dict[Priority, int] = {
    Priority.CRITICAL: 900,        # 15 minutes
    Priority.HIGH: 3600,           # 1 hour
    Priority.MEDIUM: 14400,        # 4 hours
    Priority.LOW: 86400,           # 24 hours
    Priority.INFORMATIONAL: 259200, # 3 days (best effort)
}

MAX_RETRIES = 3
RETRY_BACKOFF_BASE = 2  # seconds
DEAD_LETTER_QUEUE_MAX = 1000


@dataclass
class QueuedMessage:
    """A message in the routing queue with delivery metadata."""
    envelope: MessageEnvelope
    queued_at: float = field(default_factory=time.time)
    attempts: int = 0
    last_attempt: Optional[float] = None
    delivered: bool = False
    failed: bool = False


@dataclass
class RouteMetrics:
    """Metrics for monitoring message routing performance."""
    total_sent: int = 0
    total_delivered: int = 0
    total_failed: int = 0
    total_expired: int = 0
    avg_delivery_latency_ms: float = 0.0
    messages_by_priority: Dict[int, int] = field(default_factory=lambda: defaultdict(int))
    messages_by_type: Dict[str, int] = field(default_factory=lambda: defaultdict(int))


# ---------------------------------------------------------------------------
# Message Router
# ---------------------------------------------------------------------------

class MessageRouter:
    """
    Central message router for inter-agent communication.

    Handles:
    - Message validation and routing to registered handlers
    - Priority-based queue management with SLA enforcement
    - Retry logic with exponential backoff
    - Dead letter queue for failed messages
    - Back-pressure monitoring
    """

    def __init__(self, max_queue_depth: int = 10000):
        self._handlers: Dict[str, Callable[[MessageEnvelope], None]] = {}
        self._queues: Dict[str, List[QueuedMessage]] = defaultdict(list)
        self._dead_letter_queue: List[QueuedMessage] = []
        self._metrics = RouteMetrics()
        self._max_queue_depth = max_queue_depth
        self._protocol_version = "1.0.0"

    # -- Registration --

    def register_handler(self, agent_id: str, handler: Callable[[MessageEnvelope], None]):
        """Register a message handler for an agent."""
        self._handlers[agent_id] = handler
        logger.info(f"Registered handler for agent {agent_id}")

    def unregister_handler(self, agent_id: str):
        """Remove a message handler."""
        self._handlers.pop(agent_id, None)

    # -- Routing --

    def route(self, envelope: MessageEnvelope) -> bool:
        """
        Route a message to its recipient(s).

        Returns True if routing was successful (message queued or delivered).
        """
        # Validate protocol version
        if envelope.protocol_version != self._protocol_version:
            logger.warning(
                f"Protocol version mismatch: got {envelope.protocol_version}, "
                f"expected {self._protocol_version}"
            )

        # Check TTL
        if envelope.is_expired():
            logger.warning(f"Message {envelope.message_id} expired — dropping")
            self._metrics.total_expired += 1
            return False

        # Check retry count
        if envelope.retry_count > MAX_RETRIES:
            logger.error(
                f"Message {envelope.message_id} exceeded max retries "
                f"({envelope.retry_count}/{MAX_RETRIES}) — moving to DLQ"
            )
            self._move_to_dead_letter(envelope)
            return False

        # Route to recipients
        recipients = (
            [envelope.recipient_agent_id]
            if isinstance(envelope.recipient_agent_id, str)
            else envelope.recipient_agent_id
        )

        for recipient_id in recipients:
            self._deliver_or_queue(envelope, recipient_id)

        # Update metrics
        self._metrics.total_sent += 1
        self._metrics.messages_by_priority[envelope.priority.value] += 1
        self._metrics.messages_by_type[envelope.message_type.value] += 1

        return True

    def _deliver_or_queue(self, envelope: MessageEnvelope, recipient_id: str):
        """Try to deliver directly, or queue for later delivery."""
        if recipient_id in self._handlers:
            try:
                start = time.time()
                self._handlers[recipient_id](envelope)
                latency_ms = (time.time() - start) * 1000

                self._metrics.total_delivered += 1
                # Running average
                n = self._metrics.total_delivered
                old_avg = self._metrics.avg_delivery_latency_ms
                self._metrics.avg_delivery_latency_ms = old_avg + (latency_ms - old_avg) / n

                logger.debug(
                    f"Delivered {envelope.message_type.value} "
                    f"({envelope.message_id[:8]}) to {recipient_id} "
                    f"in {latency_ms:.1f}ms"
                )
            except Exception as e:
                logger.error(f"Delivery failed to {recipient_id}: {e}")
                self._queue_message(envelope, recipient_id)
        else:
            logger.warning(f"No handler for {recipient_id} — queuing message")
            self._queue_message(envelope, recipient_id)

    def _queue_message(self, envelope: MessageEnvelope, recipient_id: str):
        """Add a message to the recipient's queue."""
        queue = self._queues[recipient_id]
        if len(queue) >= self._max_queue_depth:
            logger.error(f"Queue for {recipient_id} full ({self._max_queue_depth})")
            self._move_to_dead_letter(envelope)
            return
        queue.append(QueuedMessage(envelope=envelope))
        logger.debug(f"Queued message for {recipient_id} (depth: {len(queue)})")

    def _move_to_dead_letter(self, envelope: MessageEnvelope):
        """Move a failed message to the dead letter queue."""
        if len(self._dead_letter_queue) >= DEAD_LETTER_QUEUE_MAX:
            self._dead_letter_queue.pop(0)  # Drop oldest
        self._dead_letter_queue.append(QueuedMessage(envelope=envelope, failed=True))
        self._metrics.total_failed += 1
        logger.error(f"Message {envelope.message_id} moved to dead letter queue")

    # -- Queue Processing --

    def process_queues(self):
        """Process queued messages — retry delivery for messages in queues."""
        for recipient_id, queue in list(self._queues.items()):
            if recipient_id not in self._handlers:
                continue

            still_queued = []
            for msg in queue:
                if msg.delivered:
                    continue

                # Check if message expired
                if msg.envelope.is_expired():
                    self._move_to_dead_letter(msg.envelope)
                    continue

                # Calculate backoff
                backoff = RETRY_BACKOFF_BASE ** msg.attempts
                elapsed = time.time() - (msg.last_attempt or msg.queued_at)

                if elapsed < backoff:
                    still_queued.append(msg)
                    continue

                # Retry delivery
                msg.attempts += 1
                msg.last_attempt = time.time()
                msg.envelope.retry_count = msg.attempts

                try:
                    self._handlers[recipient_id](msg.envelope)
                    msg.delivered = True
                    self._metrics.total_delivered += 1
                    logger.debug(f"Retry successful for {msg.envelope.message_id[:8]}")
                except Exception as e:
                    logger.warning(f"Retry {msg.attempts} failed for {msg.envelope.message_id[:8]}: {e}")
                    if msg.attempts > MAX_RETRIES:
                        self._move_to_dead_letter(msg.envelope)
                    else:
                        still_queued.append(msg)

            self._queues[recipient_id] = still_queued

    # -- SLA Monitoring --

    def check_sla_violations(self) -> List[Dict[str, Any]]:
        """Check for messages that have exceeded their SLA deadline."""
        violations = []
        now = time.time()

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

        return violations

    # -- Metrics --

    def get_metrics(self) -> Dict[str, Any]:
        """Get current routing metrics."""
        queue_depths = {k: len(v) for k, v in self._queues.items() if v}
        return {
            "total_sent": self._metrics.total_sent,
            "total_delivered": self._metrics.total_delivered,
            "total_failed": self._metrics.total_failed,
            "total_expired": self._metrics.total_expired,
            "avg_delivery_latency_ms": round(self._metrics.avg_delivery_latency_ms, 2),
            "queue_depths": queue_depths,
            "dead_letter_queue_size": len(self._dead_letter_queue),
            "sla_violations": len(self.check_sla_violations()),
        }

    def get_dead_letter_queue(self) -> List[MessageEnvelope]:
        """Retrieve messages in the dead letter queue for inspection."""
        return [msg.envelope for msg in self._dead_letter_queue]


# ---------------------------------------------------------------------------
# Singleton router
# ---------------------------------------------------------------------------

_router: Optional[MessageRouter] = None


def get_router() -> MessageRouter:
    """Get or create the global message router."""
    global _router
    if _router is None:
        _router = MessageRouter()
    return _router
