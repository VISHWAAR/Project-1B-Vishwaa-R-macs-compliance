"""
Scenario Data Generator — Creates realistic test data for all 20 compliance scenarios.

Each generator produces the input_data and context dictionaries
that feed into the orchestrator for that specific scenario.
"""

from typing import Any, Dict, List


def generate_cs01_insider_trading() -> Dict[str, Any]:
    """CS-01: Insider Trading — Pre-Announcement Accumulation"""
    return {
        "input_data": {
            "transactions": [
                {"type": "buy", "ticker": "COMPANY_X", "amount": 500000, "date": f"2025-01-{d:02d}",
                 "account_id": "PM-4201", "account_type": "personal"}
                for d in range(1, 22)
            ],
            "communications": [],
        },
        "context": {
            "tm_signals": True,
            "cs_signals": True,
            "suspicious_accumulation": True,
            "accumulation_confidence": 0.85,
            "days_before_event": 18,
            "post_event_price_change_pct": 35.0,
            "has_communication_link": True,
            "comm_confidence": 0.75,
            "communication_evidence": {
                "description": "PM attended private dinner with Company X CFO 4 weeks before acquisition announcement",
                "date": "2024-12-15",
                "channel": "private_dinner",
            },
            "misleading_statements_detected": False,
            "off_channel_detected": False,
            "chinese_wall_breach": False,
            "regulatory_change_detected": False,
            "jurisdictional_conflict": False,
            "enforcement_action": False,
        },
    }


def generate_cs02_spoofing() -> Dict[str, Any]:
    """CS-02: Market Manipulation — Spoofing in Futures Markets"""
    return {
        "input_data": {
            "transactions": [
                {"type": "limit_order", "instrument": "crude_oil_futures", "side": "buy",
                 "amount": 10000, "cancelled": True, "lifetime_ms": 350}
                for _ in range(47)
            ],
            "communications": [],
        },
        "context": {
            "tm_signals": True,
            "cs_signals": False,
            "spoofing_signals": True,
            "order_cancel_rate": 0.92,
            "avg_order_lifetime_ms": 350,
            "cancelled_large_orders": 47,
            "opposite_side_executions": 38,
            "misleading_statements_detected": False,
            "off_channel_detected": False,
            "chinese_wall_breach": False,
            "regulatory_change_detected": False,
            "jurisdictional_conflict": False,
            "enforcement_action": False,
        },
    }


def generate_cs03_unsuitable_recommendation() -> Dict[str, Any]:
    """CS-03: Unsuitable Investment Recommendation"""
    return {
        "input_data": {
            "transactions": [],
            "communications": [
                {"text": "These leveraged ETFs are safe income generators, perfect for your retirement",
                 "sender": "FA-1234", "sender_department": "advisory",
                 "recipient": f"Client-{i}", "channel": "email",
                 "is_client_facing": True}
                for i in range(12)
            ],
        },
        "context": {
            "tm_signals": False,
            "cs_signals": True,
            "misleading_statements_detected": True,
            "misleading_claims": [
                "safe income generators",
                "guaranteed returns for retirement",
            ],
            "affected_clients": 12,
            "cs_confidence": 0.80,
            "off_channel_detected": False,
            "chinese_wall_breach": False,
            "regulatory_change_detected": False,
            "jurisdictional_conflict": False,
            "enforcement_action": False,
        },
    }


def generate_cs04_aml_structuring() -> Dict[str, Any]:
    """CS-04: AML — Structuring Deposits"""
    return {
        "input_data": {
            "transactions": [
                {"type": "cash_deposit", "amount": 9500 + (i * 100), "branch_id": f"BR-{(i % 7)+1}",
                 "date": f"2025-01-{(i % 10)+1:02d}", "account_id": "COMM-4201"}
                for i in range(23)
            ],
            "communications": [],
        },
        "context": {
            "tm_signals": True,
            "cs_signals": False,
            "structuring_signals": True,
            "cash_deposits": [
                {"amount": 9500 + (i * 100), "branch_id": f"BR-{(i % 7)+1}",
                 "date": f"2025-01-{(i % 10)+1:02d}"}
                for i in range(23)
            ],
            "misleading_statements_detected": False,
            "off_channel_detected": False,
            "chinese_wall_breach": False,
            "regulatory_change_detected": False,
            "jurisdictional_conflict": False,
            "enforcement_action": False,
        },
    }


def generate_cs05_chinese_wall() -> Dict[str, Any]:
    """CS-05: Chinese Wall Breach — Information Leakage"""
    return {
        "input_data": {
            "transactions": [],
            "communications": [
                {"text": "Don't cover TechCorp next week, trust me",
                 "sender": "IB-789", "sender_department": "Investment Banking",
                 "recipient": "Research-456", "recipient_department": "Equity Research",
                 "channel": "internal_message", "is_client_facing": False},
            ],
        },
        "context": {
            "tm_signals": False,
            "cs_signals": True,
            "chinese_wall_breach": True,
            "department_1": "Investment Banking",
            "department_2": "Equity Research",
            "breach_evidence": [
                {"description": "Investment banker communicated deal-sensitive information to equity research",
                 "direction": "IB → Research", "timing": "3 days before M&A announcement"},
            ],
            "cs_confidence": 0.80,
            "info_leakage_detected": True,
            "leak_description": "Confidential M&A information leaked from IB to Research department",
            "off_channel_detected": False,
            "regulatory_change_detected": False,
            "jurisdictional_conflict": False,
            "enforcement_action": False,
        },
    }


def generate_cs06_wash_trading() -> Dict[str, Any]:
    """CS-06: Wash Trading — Cross-Account Coordination"""
    return {
        "input_data": {
            "transactions": [
                {"type": "trade", "instrument": "corp_bond_x", "amount": 100000,
                 "price": 100.01 + (i % 2) * 0.01, "buyer_account": f"ACCT-{(i % 2)+1}",
                 "seller_account": f"ACCT-{2 - (i % 2)}", "date": f"2025-01-{(i % 14)+1:02d}"}
                for i in range(34)
            ],
            "communications": [],
        },
        "context": {
            "tm_signals": True,
            "cs_signals": False,
            "wash_trading_signals": True,
            "matching_trade_pairs": 34,
            "avg_price_tolerance_bps": 2,
            "accounts_involved": 2,
            "misleading_statements_detected": False,
            "off_channel_detected": False,
            "chinese_wall_breach": False,
            "regulatory_change_detected": False,
            "jurisdictional_conflict": False,
            "enforcement_action": False,
        },
    }


def generate_cs07_regulatory_change() -> Dict[str, Any]:
    """CS-07: Regulatory Change Impact — New Margin Requirements"""
    return {
        "input_data": {
            "transactions": [],
            "communications": [],
            "regulatory_updates": [
                {"body": "SEC", "title": "Increased Initial Margin for Uncleared Swaps",
                 "effective_days": 120, "type": "final_rule"},
            ],
        },
        "context": {
            "tm_signals": False,
            "cs_signals": False,
            "ru_signals": True,
            "regulatory_change_detected": True,
            "change_details": {
                "title": "SEC Final Rule: Increased Initial Margin for Uncleared Swaps (+25%)",
                "body": "SEC",
                "regulation_id": "SEC-Swap-Margin-Rule-2025",
                "effective_date": "2025-05-01",
            },
            "impact_score": 0.7,
            "implementation_deadline_days": 120,
            "affected_jurisdictions": ["US", "EU"],
            "misleading_statements_detected": False,
            "off_channel_detected": False,
            "chinese_wall_breach": False,
            "jurisdictional_conflict": False,
            "enforcement_action": False,
        },
    }


def generate_cs08_misleading_marketing() -> Dict[str, Any]:
    """CS-08: Client Communication Violation — Misleading Performance Claims"""
    return {
        "input_data": {
            "transactions": [],
            "communications": [
                {"text": "Guaranteed 12% annual returns with zero risk of capital loss",
                 "sender": "marketing", "channel": "email", "is_client_facing": True}
                for _ in range(3400)
            ],
        },
        "context": {
            "tm_signals": False,
            "cs_signals": True,
            "misleading_statements_detected": True,
            "misleading_claims": [
                "guaranteed 12% annual returns",
                "zero risk of capital loss",
            ],
            "affected_clients": 3400,
            "cs_confidence": 0.90,
            "off_channel_detected": False,
            "chinese_wall_breach": False,
            "regulatory_change_detected": False,
            "jurisdictional_conflict": False,
            "enforcement_action": False,
        },
    }


def generate_cs09_sanctions() -> Dict[str, Any]:
    """CS-09: Sanctions Violation — Indirect Counterparty Exposure"""
    return {
        "input_data": {
            "transactions": [
                {"type": "wire_transfer", "amount": 2500000, "originator": "CLIENT-4201",
                 "beneficiary": "SUBSIDIARY_SDN_ENTITY", "intermediary_banks": 3,
                 "date": "2025-01-15"},
            ],
            "communications": [],
        },
        "context": {
            "tm_signals": True,
            "cs_signals": False,
            "ru_signals": True,
            "sanctions_signals": True,
            "sdn_match": True,
            "sdn_entity": "SUBSIDIARY_SDN_ENTITY",
            "sdn_listed_48h_ago": True,
            "misleading_statements_detected": False,
            "off_channel_detected": False,
            "chinese_wall_breach": False,
            "regulatory_change_detected": False,
            "jurisdictional_conflict": False,
            "enforcement_action": False,
        },
    }


def generate_cs10_front_running() -> Dict[str, Any]:
    """CS-10: Front-Running — Client Order Anticipation"""
    return {
        "input_data": {
            "transactions": [
                {"type": "personal_trade", "before_client_order": True,
                 "profitable": True, "minutes_before": 20, "date": f"2025-01-{d:02d}"}
                for d in range(1, 90)
            ],
            "communications": [],
        },
        "context": {
            "tm_signals": True,
            "cs_signals": False,
            "front_running_signals": True,
            "personal_trades_before_client": 79,
            "total_personal_trades": 89,
            "personal_trade_profit_rate": 0.89,
            "avg_minutes_before_client_order": 20,
            "misleading_statements_detected": False,
            "off_channel_detected": False,
            "chinese_wall_breach": False,
            "regulatory_change_detected": False,
            "jurisdictional_conflict": False,
            "enforcement_action": False,
        },
    }


def generate_cs11_data_privacy() -> Dict[str, Any]:
    """CS-11: Data Privacy Violation — Cross-Border Transfer"""
    return {
        "input_data": {"transactions": [], "communications": []},
        "context": {
            "tm_signals": False, "cs_signals": False, "ru_signals": True,
            "jurisdictional_conflict": True,
            "conflict_details": {
                "jurisdiction_a": "EU", "jurisdiction_b": "Non-Adequate Jurisdiction",
                "description": "GDPR cross-border data transfer without safeguards or SCCs",
                "regulations": ["GDPR Articles 44-49", "Schrems II"],
            },
            "ru_confidence": 0.80,
            "data_privacy_violation": True,
            "affected_records": 14000,
            "misleading_statements_detected": False,
            "off_channel_detected": False,
            "chinese_wall_breach": False,
            "regulatory_change_detected": False,
            "enforcement_action": False,
        },
    }


def generate_cs12_concentration() -> Dict[str, Any]:
    """CS-12: Concentration Risk — Portfolio Limit Breach"""
    return {
        "input_data": {"transactions": [], "communications": []},
        "context": {
            "tm_signals": True, "cs_signals": False,
            "concentration_breach": True,
            "current_concentration_pct": 28.0,
            "concentration_limit_pct": 25.0,
            "breach_duration_days": 5,
            "misleading_statements_detected": False,
            "off_channel_detected": False,
            "chinese_wall_breach": False,
            "regulatory_change_detected": False,
            "jurisdictional_conflict": False,
            "enforcement_action": False,
        },
    }


def generate_cs13_off_channel() -> Dict[str, Any]:
    """CS-13: Off-Channel Communication — Personal Device Usage"""
    return {
        "input_data": {"transactions": [], "communications": []},
        "context": {
            "tm_signals": False, "cs_signals": True,
            "off_channel_detected": True,
            "affected_representatives": 7,
            "off_channel_types": ["WhatsApp", "personal SMS"],
            "cs_confidence": 0.82,
            "misleading_statements_detected": False,
            "chinese_wall_breach": False,
            "regulatory_change_detected": False,
            "jurisdictional_conflict": False,
            "enforcement_action": False,
        },
    }


def generate_cs14_late_trading() -> Dict[str, Any]:
    """CS-14: Late Trading — Mutual Fund NAV Manipulation"""
    return {
        "input_data": {
            "transactions": [
                {"type": "mutual_fund_purchase", "timestamp": "16:12:00",
                 "system_entry": "16:12:00", "date": "2025-01-15"}
                for _ in range(14)
            ],
            "communications": [],
        },
        "context": {
            "tm_signals": True, "cs_signals": False,
            "late_trading_signals": True,
            "late_order_count": 14,
            "cutoff_time": "16:00:00",
            "max_delay_minutes": 23,
            "misleading_statements_detected": False,
            "off_channel_detected": False,
            "chinese_wall_breach": False,
            "regulatory_change_detected": False,
            "jurisdictional_conflict": False,
            "enforcement_action": False,
        },
    }


def generate_cs15_best_execution() -> Dict[str, Any]:
    """CS-15: Best Execution Failure — Systematic Order Routing Bias"""
    return {
        "input_data": {"transactions": [], "communications": []},
        "context": {
            "tm_signals": True, "cs_signals": False,
            "best_execution_signals": True,
            "single_venue_routing_pct": 78,
            "better_price_venues": 3,
            "avg_price_improvement_cents": 1.0,
            "analysis_period_days": 90,
            "misleading_statements_detected": False,
            "off_channel_detected": False,
            "chinese_wall_breach": False,
            "regulatory_change_detected": False,
            "jurisdictional_conflict": False,
            "enforcement_action": False,
        },
    }


def generate_cs16_research_independence() -> Dict[str, Any]:
    """CS-16: Conflict of Interest — Research Independence"""
    return {
        "input_data": {
            "transactions": [],
            "communications": [
                {"text": "Meeting with IB team to discuss TechCorp secondary offering strategy",
                 "sender": "RA-789", "sender_department": "Research",
                 "recipient": "IB-456", "recipient_department": "Investment Banking",
                 "channel": "internal_message", "is_client_facing": False,
                 "date": "2025-01-12"},
            ],
        },
        "context": {
            "tm_signals": True, "cs_signals": True,
            "chinese_wall_breach": True,
            "department_1": "Research",
            "department_2": "Investment Banking",
            "breach_evidence": [
                {"description": "Research analyst met with IB team 3 days before rating change",
                 "direction": "Research ↔ IB", "timing": "3 days before secondary offering"},
            ],
            "cs_confidence": 0.85,
            "info_leakage_detected": True,
            "leak_description": "Research independence compromised by IB interaction before rating change",
            "misleading_statements_detected": False,
            "off_channel_detected": False,
            "regulatory_change_detected": False,
            "jurisdictional_conflict": False,
            "enforcement_action": False,
        },
    }


def generate_cs17_elder_exploitation() -> Dict[str, Any]:
    """CS-17: Elder Financial Exploitation"""
    return {
        "input_data": {
            "transactions": [
                {"type": "trade", "account_id": "ELDER-8801", "count": 47,
                 "avg_historical": 2, "account_decline_pct": 22}
            ],
            "communications": [
                {"text": "Execute all trades as instructed by POA holder",
                 "sender": "POA-HOLDER", "channel": "phone_transcript",
                 "is_client_facing": False}
            ],
        },
        "context": {
            "tm_signals": True, "cs_signals": True,
            "elder_exploitation_signals": True,
            "exploitation_evidence": "84-year-old client: 47 trades in one month (avg: 2/month), "
                                   "new POA filed 6 weeks ago, account declined 22%",
            "cs_confidence": 0.80,
            "misleading_statements_detected": False,
            "off_channel_detected": False,
            "chinese_wall_breach": False,
            "regulatory_change_detected": False,
            "jurisdictional_conflict": False,
            "enforcement_action": False,
        },
    }


def generate_cs18_false_positive() -> Dict[str, Any]:
    """CS-18: FALSE POSITIVE — Legitimate Block Trade (must NOT alert)"""
    return {
        "input_data": {
            "transactions": [
                {"type": "block_trade", "amount": 450000000, "adv_pct": 8,
                 "pre_arranged": True, "documented": True,
                 "portfolio_rebalancing": True, "disclosed": True}
            ],
            "communications": [],
        },
        "context": {
            "tm_signals": True,
            "cs_signals": False,
            "is_false_positive": True,
            "fp_verification": {
                "is_legitimate": True,
                "reason": "Pre-arranged block trade with proper documentation, "
                         "part of disclosed portfolio rebalancing programme",
            },
            "misleading_statements_detected": False,
            "off_channel_detected": False,
            "chinese_wall_breach": False,
            "regulatory_change_detected": False,
            "jurisdictional_conflict": False,
            "enforcement_action": False,
        },
    }


def generate_cs19_multi_jurisdiction() -> Dict[str, Any]:
    """CS-19: Multi-Jurisdiction Regulatory Conflict"""
    return {
        "input_data": {"transactions": [], "communications": [],
                       "regulatory_updates": [
                           {"body": "EU", "title": "EMIR OTC Derivative Reporting (1 day)"},
                           {"body": "MAS", "title": "Cross-Border Data Sharing Restriction"},
                       ]},
        "context": {
            "tm_signals": False, "cs_signals": False, "ru_signals": True,
            "jurisdictional_conflict": True,
            "conflict_details": {
                "jurisdiction_a": "EU",
                "jurisdiction_b": "Singapore",
                "description": "EU mandates OTC derivative reporting within 1 business day, "
                             "but Singapore restricts cross-border sharing of client derivative data",
                "regulations": ["EMIR Reporting Obligation", "MAS Securities and Futures Act", "GDPR"],
            },
            "ru_confidence": 0.80,
            "misleading_statements_detected": False,
            "off_channel_detected": False,
            "chinese_wall_breach": False,
            "regulatory_change_detected": False,
            "enforcement_action": False,
        },
    }


def generate_cs20_coordinated() -> Dict[str, Any]:
    """CS-20: Coordinated — Complex Money Laundering through Trade Finance"""
    return {
        "input_data": {
            "transactions": [
                {"type": "letter_of_credit", "amount": 3000000, "market_value": 750000,
                 "price_inflation_pct": 300, "beneficiary_jurisdiction": "high_risk",
                 "intermediary_banks": 5, "compliance_flags_overridden": 2}
            ],
            "communications": [
                {"text": "Override compliance screening for this client, they are a priority relationship",
                 "sender": "RM-456", "sender_department": "Relationship Management",
                 "channel": "internal_message", "is_client_facing": False},
            ],
            "regulatory_updates": [
                {"body": "FATF", "title": "Enhanced Due Diligence - Country Added to Watchlist"},
            ],
        },
        "context": {
            "tm_signals": True, "cs_signals": True, "ru_signals": True,
            "structuring_signals": True,
            "cash_deposits": [],

            "chinese_wall_breach": True,
            "department_1": "Relationship Management",
            "department_2": "Compliance",
            "breach_evidence": [
                {"description": "Relationship manager overrode compliance screening flags twice",
                 "direction": "RM → Compliance override"},
            ],
            "cs_confidence": 0.85,

            "regulatory_change_detected": True,
            "change_details": {
                "title": "FATF Enhanced Due Diligence - Beneficiary country added to watchlist",
                "body": "FATF",
                "regulation_id": "FATF-EDD-2025",
            },
            "impact_score": 0.8,
            "implementation_deadline_days": 30,
            "affected_jurisdictions": ["US", "EU", "Singapore"],

            "enforcement_action": False,
            "jurisdictional_conflict": False,
            "misleading_statements_detected": False,
            "off_channel_detected": False,
        },
    }


# ---------------------------------------------------------------------------
# Scenario Registry
# ---------------------------------------------------------------------------

SCENARIO_GENERATORS = {
    "CS-01": generate_cs01_insider_trading,
    "CS-02": generate_cs02_spoofing,
    "CS-03": generate_cs03_unsuitable_recommendation,
    "CS-04": generate_cs04_aml_structuring,
    "CS-05": generate_cs05_chinese_wall,
    "CS-06": generate_cs06_wash_trading,
    "CS-07": generate_cs07_regulatory_change,
    "CS-08": generate_cs08_misleading_marketing,
    "CS-09": generate_cs09_sanctions,
    "CS-10": generate_cs10_front_running,
    "CS-11": generate_cs11_data_privacy,
    "CS-12": generate_cs12_concentration,
    "CS-13": generate_cs13_off_channel,
    "CS-14": generate_cs14_late_trading,
    "CS-15": generate_cs15_best_execution,
    "CS-16": generate_cs16_research_independence,
    "CS-17": generate_cs17_elder_exploitation,
    "CS-18": generate_cs18_false_positive,
    "CS-19": generate_cs19_multi_jurisdiction,
    "CS-20": generate_cs20_coordinated,
}


def generate_scenario_data(scenario_id: str) -> Dict[str, Any]:
    """Generate test data for a specific scenario."""
    generator = SCENARIO_GENERATORS.get(scenario_id)
    if not generator:
        raise ValueError(f"Unknown scenario: {scenario_id}")
    return generator()
# Scenarios update
# More scenarios
