"""
Transaction Monitor Agent (TM-001)

Continuous surveillance of trading and financial transaction activity.
Detects: insider trading, market manipulation, spoofing/layering, wash trading,
front-running, AML structuring, sanctions violations, concentration risk,
late trading, best execution failures.

Architecture: LangGraph sub-graph with internal processing nodes.
"""

import json
import math
import os
import time
import logging
from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime, timezone
from collections import defaultdict

from langchain_core.messages import HumanMessage, SystemMessage

from observability.logger import get_structured_logger, Severity, LogCategory
from observability.audit_trail import get_audit_trail
from protocols.message_schema import (
    AgentID, AlertSeverity, ViolationType,
    MessageEnvelope, MessageType, Priority, AuditClassification,
    DetectionEvidence, create_detection_message,
)

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Detection Rules
# ---------------------------------------------------------------------------

# Insider Trading Detection Rules
INSIDER_TRADING_RULES = {
    "accumulation_period_days": 21,
    "price_increase_threshold_pct": 20.0,
    "position_size_percentile": 95,
    "connection_window_days": 30,
}

# Spoofing Detection Rules
SPOOFING_RULES = {
    "cancel_rate_threshold": 0.85,
    "order_lifetime_ms_max": 500,
    "min_spoof_count": 5,
    "opposite_side_execute_ratio": 0.7,
}

# AML Structuring Rules
AML_STRUCTURING_RULES = {
    "cash_threshold_usd": 10000,
    "structuring_range_usd": (8000, 9999),
    "min_deposits": 3,
    "time_window_days": 10,
    "branch_count_threshold": 3,
}

# Wash Trading Rules
WASH_TRADING_RULES = {
    "matching_trade_min": 5,
    "price_tolerance_bps": 5,
    "time_window_days": 14,
    "volume_threshold": 0.8,
}

# Concentration Risk Rules
CONCENTRATION_RULES = {
    "sector_limit_pct": 25.0,
    "breach_persist_days": 3,
    "material_exceedance_pts": 10.0,  # breach >= this many pts is treated as HIGH severity
}

# Sanctions Screening Rules (TM side — partial detection awaiting RU confirmation)
SANCTIONS_RULES = {
    "screening_confidence": 0.70,  # partial — sanctions match requires RU coordination
    "max_intermediary_banks": 1,   # chains longer than this are high-risk routing
}

# Front-Running Rules
FRONT_RUNNING_RULES = {
    "personal_trade_before_client_minutes": 30,
    "profit_rate_threshold": 0.80,
    "min_trades": 20,
    "correlation_threshold": 0.7,
}


# ---------------------------------------------------------------------------
# Detection Engine
# ---------------------------------------------------------------------------

class TransactionMonitor:
    """
    Transaction Monitor agent — detects compliance violations in transaction data.

    Internal processing pipeline:
    1. Pattern Detection — statistical anomaly detection
    2. Threshold Monitoring — regulatory threshold compliance
    3. Temporal Analysis — cross-time-window pattern correlation
    4. Counterparty Analysis — unusual counterparty concentrations
    5. Cross-Market Surveillance — correlated multi-venue patterns
    """

    def __init__(self):
        self._log = get_structured_logger()
        self._audit = get_audit_trail()
        self._agent_id = AgentID.TRANSACTION_MONITOR.value
        self._detection_history: List[Dict[str, Any]] = []
        self._false_positive_rate = 0.05  # 5% baseline FP rate

    def analyze_transaction_batch(
        self,
        transactions: List[Dict[str, Any]],
        scenario_id: str = "",
        context: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Analyze a batch of transactions and return detection events.

        Args:
            transactions: List of transaction records
            scenario_id: Which scenario this is for
            context: Additional context (e.g. company info, positions)

        Returns:
            List of detection events
        """
        start_time = time.time()
        detections = []

        # Run all detection pipelines
        detections.extend(self._detect_insider_trading(transactions, context or {}))
        detections.extend(self._detect_spoofing(transactions, context or {}))
        detections.extend(self._detect_aml_structuring(transactions, context or {}))
        detections.extend(self._detect_wash_trading(transactions, context or {}))
        detections.extend(self._detect_concentration_risk(transactions, context or {}))
        detections.extend(self._detect_sanctions(transactions, context or {}))
        detections.extend(self._detect_front_running(transactions, context or {}))
        detections.extend(self._detect_late_trading(transactions, context or {}))
        detections.extend(self._detect_best_execution(transactions, context or {}))

        elapsed_ms = (time.time() - start_time) * 1000

        # Log performance
        self._log.performance_metric(
            self._agent_id, "batch_analysis_latency_ms", round(elapsed_ms, 2)
        )

        # Annotate with timing
        for det in detections:
            det["detection_latency_ms"] = elapsed_ms
            det["scenario_id"] = scenario_id
            det["agent_id"] = self._agent_id

        self._detection_history.extend(detections)
        return detections

    def _detect_insider_trading(
        self, transactions: List[Dict], context: Dict
    ) -> List[Dict]:
        """Detect pre-announcement accumulation patterns."""
        detections = []

        # Check for pattern: accumulation → material event → price spike
        if context.get("suspicious_accumulation", False):
            confidence = context.get("accumulation_confidence", 0.7)
            days_before = context.get("days_before_event", 0)
            price_increase = context.get("post_event_price_change_pct", 0)

            if (days_before <= INSIDER_TRADING_RULES["accumulation_period_days"] and
                price_increase >= INSIDER_TRADING_RULES["price_increase_threshold_pct"]):

                evidence = [
                    DetectionEvidence(
                        source="transaction_log",
                        timestamp=datetime.now(timezone.utc).isoformat(),
                        description=f"Accumulation pattern detected over {days_before} days before event",
                        data={"days_before": days_before, "price_change": price_increase},
                        confidence=confidence,
                    ).model_dump()
                ]

                if context.get("has_communication_link", False):
                    evidence.append(DetectionEvidence(
                        source="communication_scan",
                        timestamp=datetime.now(timezone.utc).isoformat(),
                        description="Communication link between trader and company insider detected",
                        data=context.get("communication_evidence", {}),
                        confidence=context.get("comm_confidence", 0.6),
                    ).model_dump())
                    confidence = min(0.95, confidence + 0.15)

                detections.append({
                    "violation_type": ViolationType.INSIDER_TRADING.value,
                    "severity": AlertSeverity.CRITICAL.value,
                    "confidence": confidence,
                    "description": f"Pre-announcement accumulation detected: {days_before} days before event, "
                                  f"{price_increase:.1f}% price increase",
                    "evidence": evidence,
                    "regulations": ["SEC Rule 10b-5", "FINRA Rule 2010", "Insider Trading Sanctions Act"],
                    "jurisdictions": ["US"],
                })

        return detections

    def _detect_spoofing(
        self, transactions: List[Dict], context: Dict
    ) -> List[Dict]:
        """Detect spoofing/layering patterns in order data."""
        detections = []

        if context.get("spoofing_signals", False):
            cancel_rate = context.get("order_cancel_rate", 0)
            order_lifetime_ms = context.get("avg_order_lifetime_ms", 1000)
            spoof_count = context.get("cancelled_large_orders", 0)
            opposite_executions = context.get("opposite_side_executions", 0)

            confidence = 0.0
            if cancel_rate >= SPOOFING_RULES["cancel_rate_threshold"]:
                confidence += 0.3
            if order_lifetime_ms <= SPOOFING_RULES["order_lifetime_ms_max"]:
                confidence += 0.3
            if spoof_count >= SPOOFING_RULES["min_spoof_count"]:
                confidence += 0.2
            if opposite_executions > 0:
                confidence += 0.2

            confidence = min(0.95, confidence)

            if confidence > 0.3:
                detections.append({
                    "violation_type": ViolationType.SPOOFING_LAYERING.value,
                    "severity": AlertSeverity.HIGH.value,
                    "confidence": confidence,
                    "description": f"Potential spoofing detected: {cancel_rate:.1%} cancel rate, "
                                  f"{spoof_count} cancelled large orders, "
                                  f"{opposite_executions} opposite-side executions",
                    "evidence": [DetectionEvidence(
                        source="order_book_analysis",
                        timestamp=datetime.now(timezone.utc).isoformat(),
                        description=f"Order pattern analysis: {spoof_count} large orders cancelled "
                                   f"within {order_lifetime_ms:.0f}ms",
                        data=context,
                        confidence=confidence,
                    ).model_dump()],
                    "regulations": ["Dodd-Frank Act Section 747", "CEA Section 4c(a)(5)", "CME Rule 575"],
                    "jurisdictions": ["US"],
                })

        return detections

    def _detect_aml_structuring(
        self, transactions: List[Dict], context: Dict
    ) -> List[Dict]:
        """Detect currency structuring (smurfing) patterns."""
        detections = []

        if context.get("structuring_signals", False):
            cash_deposits = context.get("cash_deposits", [])
            total_amount = sum(d.get("amount", 0) for d in cash_deposits)
            deposit_count = len(cash_deposits)
            branches_used = len(set(d.get("branch_id", "") for d in cash_deposits))

            # Check for deposits just below reporting threshold
            structured_count = sum(
                1 for d in cash_deposits
                if AML_STRUCTURING_RULES["structuring_range_usd"][0]
                <= d.get("amount", 0)
                <= AML_STRUCTURING_RULES["structuring_range_usd"][1]
            )

            confidence = 0.0
            if deposit_count >= AML_STRUCTURING_RULES["min_deposits"]:
                confidence += 0.3
            if structured_count >= AML_STRUCTURING_RULES["min_deposits"]:
                confidence += 0.3
            if branches_used >= AML_STRUCTURING_RULES["branch_count_threshold"]:
                confidence += 0.2
            if total_amount > 100000:
                confidence += 0.2

            confidence = min(0.95, confidence)

            if confidence > 0.3:
                detections.append({
                    "violation_type": ViolationType.AML_STRUCTURING.value,
                    "severity": AlertSeverity.CRITICAL.value,
                    "confidence": confidence,
                    "description": f"Suspected currency structuring: {deposit_count} cash deposits "
                                  f"totalling ${total_amount:,.0f} across {branches_used} branches, "
                                  f"{structured_count} deposits just below $10K threshold",
                    "evidence": [DetectionEvidence(
                        source="transaction_log",
                        timestamp=datetime.now(timezone.utc).isoformat(),
                        description=f"Cash deposit pattern analysis: {structured_count}/{deposit_count} "
                                   f"deposits in structuring range (${AML_STRUCTURING_RULES['structuring_range_usd'][0]:,}-"
                                   f"${AML_STRUCTURING_RULES['structuring_range_usd'][1]:,})",
                        data={"deposits": cash_deposits, "total": total_amount},
                        confidence=confidence,
                    ).model_dump()],
                    "regulations": ["Bank Secrecy Act", "31 CFR 1020.320", "FinCEN SAR requirements"],
                    "jurisdictions": ["US"],
                    "requires_sar": True,
                })

        return detections

    def _detect_wash_trading(
        self, transactions: List[Dict], context: Dict
    ) -> List[Dict]:
        """Detect wash trading patterns."""
        detections = []

        if context.get("wash_trading_signals", False):
            matching_pairs = context.get("matching_trade_pairs", 0)
            price_tolerance = context.get("avg_price_tolerance_bps", 0)
            accounts_involved = context.get("accounts_involved", 0)

            confidence = 0.0
            if matching_pairs >= WASH_TRADING_RULES["matching_trade_min"]:
                confidence += 0.4
            if price_tolerance <= WASH_TRADING_RULES["price_tolerance_bps"]:
                confidence += 0.3
            if accounts_involved >= 2:
                confidence += 0.3

            confidence = min(0.95, confidence)
            if confidence > 0.3:
                detections.append({
                    "violation_type": ViolationType.WASH_TRADING.value,
                    "severity": AlertSeverity.HIGH.value,
                    "confidence": confidence,
                    "description": f"Suspected wash trading: {matching_pairs} matching trades between "
                                  f"{accounts_involved} accounts, avg tolerance {price_tolerance:.1f} bps",
                    "evidence": [DetectionEvidence(
                        source="cross_account_analysis",
                        timestamp=datetime.now(timezone.utc).isoformat(),
                        description=f"Trade matching analysis across {accounts_involved} accounts",
                        data=context,
                        confidence=confidence,
                    ).model_dump()],
                    "regulations": ["CEA Section 4c(a)", "SEC Rule 10b-5", "FINRA Rule 5210"],
                    "jurisdictions": ["US"],
                })

        return detections

    def _detect_concentration_risk(
        self, transactions: List[Dict], context: Dict
    ) -> List[Dict]:
        """Detect portfolio concentration limit breaches."""
        detections = []

        if context.get("concentration_breach", False):
            current_pct = context.get("current_concentration_pct", 0)
            limit_pct = context.get("concentration_limit_pct", CONCENTRATION_RULES["sector_limit_pct"])
            breach_days = context.get("breach_duration_days", 0)

            exceedance = current_pct - limit_pct

            if exceedance > 0:
                # Confidence grows with the size of the breach and how long it persists.
                # e.g. 3pt breach persisting 5 days -> 0.5 + 0.12 + 0.10 = 0.72
                confidence = min(
                    0.95,
                    0.5 + 0.04 * exceedance + 0.02 * min(breach_days, 5),
                )

                # MEDIUM by default; HIGH only when the breach is material
                # (>= 10 percentage points over the limit), regardless of persistence.
                severity = (
                    AlertSeverity.HIGH.value
                    if exceedance >= CONCENTRATION_RULES["material_exceedance_pts"]
                    else AlertSeverity.MEDIUM.value
                )

                detections.append({
                    "violation_type": ViolationType.CONCENTRATION_RISK.value,
                    "severity": severity,
                    "confidence": confidence,
                    "description": f"Concentration limit breach: {current_pct:.1f}% vs {limit_pct:.1f}% limit, "
                                  f"persisting for {breach_days} days",
                    "evidence": [DetectionEvidence(
                        source="portfolio_analysis",
                        timestamp=datetime.now(timezone.utc).isoformat(),
                        description=f"Sector concentration {current_pct:.1f}% exceeds limit {limit_pct:.1f}%",
                        data={"current_pct": current_pct, "limit_pct": limit_pct, "breach_days": breach_days},
                        confidence=confidence,
                    ).model_dump()],
                    "regulations": ["Investment Company Act Section 13", "SEC Form N-PORT", "UCITS concentration limits"],
                    "jurisdictions": ["US", "EU"],
                })

        return detections

    def _detect_sanctions(
        self, transactions: List[Dict], context: Dict
    ) -> List[Dict]:
        """
        Detect wire transfers to SDN-listed beneficiaries.

        The TM signals the transaction pattern (high-risk beneficiary, long
        intermediary chain) but the sanctions match itself requires RU
        coordination — hence the partial (0.70) confidence.
        """
        detections = []

        if not (context.get("sanctions_signals", False) or context.get("sdn_match", False)):
            return detections

        wires = [t for t in transactions if t.get("type") == "wire_transfer"]
        sdn_entity = context.get("sdn_entity", "")

        for wire in wires:
            beneficiary = wire.get("beneficiary", "")
            if not beneficiary:
                continue
            # Only flag wires where the beneficiary matches the SDN-listed entity
            if sdn_entity and beneficiary != sdn_entity:
                continue

            intermediary_banks = wire.get("intermediary_banks", 0)
            detections.append({
                "violation_type": ViolationType.SANCTIONS_VIOLATION.value,
                "severity": AlertSeverity.HIGH.value,
                "confidence": SANCTIONS_RULES["screening_confidence"],
                "description": (
                    f"Wire transfer to SDN-listed beneficiary {beneficiary} routed through "
                    f"{intermediary_banks} intermediary banks — sanctions match pending RU confirmation"
                ),
                "evidence": [DetectionEvidence(
                    source="sanctions_screening",
                    timestamp=datetime.now(timezone.utc).isoformat(),
                    description=(
                        f"Beneficiary {beneficiary} matches SDN list entity"
                        if sdn_entity else
                        "High-risk beneficiary flagged for sanctions screening"
                    ),
                    data={"beneficiary": beneficiary, "intermediary_banks": intermediary_banks},
                    confidence=SANCTIONS_RULES["screening_confidence"],
                ).model_dump()],
                "regulations": ["OFAC Regulations", "31 CFR Part 501", "EU Sanctions Regulation"],
                "jurisdictions": ["US"],
            })

        return detections

    def _detect_front_running(
        self, transactions: List[Dict], context: Dict
    ) -> List[Dict]:
        """Detect front-running patterns."""
        detections = []

        if context.get("front_running_signals", False):
            before_client_count = context.get("personal_trades_before_client", 0)
            total_personal = context.get("total_personal_trades", 0)
            profit_rate = context.get("personal_trade_profit_rate", 0)
            avg_minutes_before = context.get("avg_minutes_before_client_order", 0)

            if total_personal < FRONT_RUNNING_RULES["min_trades"]:
                return detections

            ratio = before_client_count / total_personal if total_personal > 0 else 0

            confidence = 0.0
            if ratio >= FRONT_RUNNING_RULES["correlation_threshold"]:
                confidence += 0.4
            if profit_rate >= FRONT_RUNNING_RULES["profit_rate_threshold"]:
                confidence += 0.3
            if avg_minutes_before <= FRONT_RUNNING_RULES["personal_trade_before_client_minutes"]:
                confidence += 0.3

            confidence = min(0.95, confidence)
            if confidence > 0.3:
                detections.append({
                    "violation_type": ViolationType.FRONT_RUNNING.value,
                    "severity": AlertSeverity.CRITICAL.value,
                    "confidence": confidence,
                    "description": f"Potential front-running: {before_client_count}/{total_personal} "
                                  f"personal trades before client orders, {profit_rate:.1%} profit rate",
                    "evidence": [DetectionEvidence(
                        source="order_sequence_analysis",
                        timestamp=datetime.now(timezone.utc).isoformat(),
                        description=f"Order timing analysis: avg {avg_minutes_before:.0f} min before client orders",
                        data=context,
                        confidence=confidence,
                    ).model_dump()],
                    "regulations": ["SEC Section 17(j)", "FINRA Rule 5270"],
                    "jurisdictions": ["US"],
                })

        return detections

    def _detect_late_trading(
        self, transactions: List[Dict], context: Dict
    ) -> List[Dict]:
        """Detect late trading in mutual fund orders."""
        detections = []

        if context.get("late_trading_signals", False):
            late_orders = context.get("late_order_count", 0)
            cutoff_time = context.get("cutoff_time", "16:00:00")
            max_delay_minutes = context.get("max_delay_minutes", 0)

            confidence = min(0.95, 0.5 + late_orders * 0.05) if late_orders > 0 else 0

            if late_orders > 0 and confidence > 0.3:
                detections.append({
                    "violation_type": ViolationType.LATE_TRADING.value,
                    "severity": AlertSeverity.CRITICAL.value,
                    "confidence": confidence,
                    "description": f"Potential late trading: {late_orders} mutual fund orders "
                                  f"executed after {cutoff_time} cutoff, max delay {max_delay_minutes:.0f} min",
                    "evidence": [DetectionEvidence(
                        source="order_timestamp_analysis",
                        timestamp=datetime.now(timezone.utc).isoformat(),
                        description=f"Order timing vs NAV cutoff analysis",
                        data=context,
                        confidence=confidence,
                    ).model_dump()],
                    "regulations": ["SEC Rule 22c-1", "Investment Company Act Section 22(c)"],
                    "jurisdictions": ["US"],
                })

        return detections

    def _detect_best_execution(
        self, transactions: List[Dict], context: Dict
    ) -> List[Dict]:
        """Detect systematic best execution failures."""
        detections = []

        if context.get("best_execution_signals", False):
            single_venue_pct = context.get("single_venue_routing_pct", 0)
            better_venues = context.get("better_price_venues", 0)
            avg_price_improvement = context.get("avg_price_improvement_cents", 0)
            analysis_days = context.get("analysis_period_days", 0)

            confidence = 0.0
            if single_venue_pct > 70:
                confidence += 0.4
            if better_venues > 1:
                confidence += 0.3
            if avg_price_improvement > 0.5:
                confidence += 0.3

            confidence = min(0.95, confidence)
            if confidence > 0.3:
                detections.append({
                    "violation_type": ViolationType.BEST_EXECUTION_FAILURE.value,
                    "severity": AlertSeverity.HIGH.value,
                    "confidence": confidence,
                    "description": f"Systematic best execution failure: {single_venue_pct:.0f}% routed "
                                  f"to single venue, {better_venues} better-priced venues available "
                                  f"({avg_price_improvement:.2f}¢/share improvement missed)",
                    "evidence": [DetectionEvidence(
                        source="order_routing_analysis",
                        timestamp=datetime.now(timezone.utc).isoformat(),
                        description=f"Order routing analysis over {analysis_days} days",
                        data=context,
                        confidence=confidence,
                    ).model_dump()],
                    "regulations": ["SEC Rule 606", "FINRA Rule 5310", "MiFID II Best Execution"],
                    "jurisdictions": ["US", "EU"],
                })

        return detections

    def check_false_positive(
        self,
        detection: Dict[str, Any],
        verification_data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Verify whether a detection is a false positive.

        Used for CS-18 (legitimate block trade) scenario.
        Returns the detection with updated status.
        """
        if verification_data.get("is_legitimate", False):
            return {
                **detection,
                "is_false_positive": True,
                "severity": AlertSeverity.NO_ALERT.value,
                "confidence": 0.0,
                "fp_reason": verification_data.get("reason", "Verified legitimate activity"),
                "description": f"FALSE POSITIVE — {detection.get('description', '')}: "
                              f"{verification_data.get('reason', 'Verified as legitimate')}",
            }
        return detection
