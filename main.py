"""
MACS — Multi-Agent Compliance Monitoring System — Challenge Runner

Runs all 20 compliance scenarios through the complete multi-agent pipeline.
Outputs results and prints a summary.

Usage:
    python main.py              # Run all 20 scenarios
    python main.py 1 5 18       # Run specific scenarios only
    python main.py --summary    # Print evaluation dashboard only
"""

import json
import os
import sys
import time
import logging
from typing import Any, Dict, List, Optional
from datetime import datetime

# Fix Windows console encoding
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO, format="%(message)s")

from agents.orchestrator import run_scenario, get_orchestrator
from data.generators import generate_scenario_data, SCENARIO_GENERATORS
from observability.dashboard import ComplianceDashboard

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Scenario metadata
# ---------------------------------------------------------------------------

SCENARIO_META = {
    1:  {"title": "Insider Trading", "agents": "TM + CS", "complexity": "High", "alert": "CRITICAL"},
    2:  {"title": "Spoofing", "agents": "TM", "complexity": "Medium", "alert": "HIGH"},
    3:  {"title": "Unsuitable Recommendation", "agents": "CS + TM", "complexity": "High", "alert": "HIGH"},
    4:  {"title": "AML Structuring", "agents": "TM", "complexity": "Medium", "alert": "CRITICAL"},
    5:  {"title": "Chinese Wall Breach", "agents": "CS", "complexity": "High", "alert": "CRITICAL"},
    6:  {"title": "Wash Trading", "agents": "TM", "complexity": "High", "alert": "HIGH"},
    7:  {"title": "Regulatory Change", "agents": "RU", "complexity": "Medium", "alert": "MEDIUM"},
    8:  {"title": "Misleading Marketing", "agents": "CS", "complexity": "Low-Medium", "alert": "CRITICAL"},
    9:  {"title": "Sanctions Violation", "agents": "TM + RU", "complexity": "High", "alert": "CRITICAL"},
    10: {"title": "Front-Running", "agents": "TM", "complexity": "Medium", "alert": "CRITICAL"},
    11: {"title": "Data Privacy", "agents": "CS + RU", "complexity": "Medium", "alert": "HIGH"},
    12: {"title": "Concentration Risk", "agents": "TM", "complexity": "Low", "alert": "MEDIUM"},
    13: {"title": "Off-Channel Comms", "agents": "CS", "complexity": "Medium", "alert": "HIGH"},
    14: {"title": "Late Trading", "agents": "TM", "complexity": "Medium", "alert": "CRITICAL"},
    15: {"title": "Best Execution", "agents": "TM", "complexity": "Medium", "alert": "HIGH"},
    16: {"title": "Research Independence", "agents": "CS + TM", "complexity": "High", "alert": "CRITICAL"},
    17: {"title": "Elder Exploitation", "agents": "TM + CS", "complexity": "High", "alert": "CRITICAL"},
    18: {"title": "FALSE POSITIVE", "agents": "TM", "complexity": "Medium", "alert": "NO ALERT"},
    19: {"title": "Multi-Jurisdiction Conflict", "agents": "RU", "complexity": "High", "alert": "HIGH"},
    20: {"title": "Coordinated AML", "agents": "ALL FOUR", "complexity": "Very High", "alert": "CRITICAL"},
}


def run_single_scenario(scenario_num: int) -> Dict[str, Any]:
    """Run a single scenario and return the result."""
    scenario_id = f"CS-{scenario_num:02d}"
    meta = SCENARIO_META[scenario_num]
    print(f"\n{'='*70}")
    print(f"  SCENARIO {scenario_id}: {meta['title']}")
    print(f"  Agents: {meta['agents']} | Complexity: {meta['complexity']} | Expected: {meta['alert']}")
    print(f"{'='*70}\n")

    # Generate test data
    data = generate_scenario_data(scenario_id)

    # Run through orchestrator
    start = time.time()
    result = run_scenario(
        scenario_id=scenario_id,
        input_data=data["input_data"],
        context=data["context"],
    )
    elapsed = time.time() - start

    # Extract key results
    consensus = result.get("consensus_result", {})
    escalation = result.get("escalation")
    detections = result.get("all_detections", [])

    # Print results
    print(f"  Detections: {len(detections)}")
    for det in detections:
        is_fp = " [FALSE POSITIVE]" if det.get("is_false_positive") else ""
        print(f"    - {det.get('violation_type', '?')} | "
              f"Severity: {det.get('severity', '?')} | "
              f"Confidence: {det.get('confidence', 0):.2f}{is_fp}")

    print(f"\n  Consensus: {consensus.get('final_decision', 'N/A')} "
          f"(confidence: {consensus.get('overall_confidence', 0):.2f})")
    print(f"  Escalation: {'Tier ' + str(escalation['current_tier']) if escalation else 'None'}")
    print(f"  Reports: {len(result.get('reports', {}))}")
    print(f"  Audit Trail: {len(result.get('audit_entries', []))} entries")
    print(f"  Duration: {elapsed:.2f}s")
    print(f"  Errors: {len(result.get('error_log', []))}")

    # Special handling for CS-18
    if scenario_num == 18:
        false_positives = [d for d in detections if d.get("is_false_positive")]
        if false_positives:
            print(f"\n  ✅ CS-18 CORRECTLY HANDLED: False positive suppressed")
        elif escalation:
            print(f"\n  ❌ CS-18 INCORRECTLY ESCALATED: Should NOT have escalated (-25 penalty)")
        else:
            print(f"\n  ✅ CS-18 CORRECTLY: No escalation")

    return {
        "scenario_id": scenario_id,
        "meta": meta,
        "result": result,
        "elapsed": elapsed,
        "consensus_decision": consensus.get("final_decision", "unknown"),
        "escalated": escalation is not None,
    }


def run_all_scenarios(ids=None):
    """Run all (or selected) scenarios and print a summary."""
    print(f"\n{'#'*70}")
    print(f"  MACS — Multi-Agent Compliance Monitoring System")
    print(f"  Scenario Runner")
    print(f"  Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'#'*70}")

    scenario_ids = ids if ids else list(range(1, 21))
    all_results = []

    for num in scenario_ids:
        if num not in SCENARIO_META:
            print(f"\n  ⚠ Skipping invalid scenario: {num}")
            continue
        try:
            result = run_single_scenario(num)
            all_results.append(result)
        except Exception as e:
            print(f"\n  ❌ Scenario CS-{num:02d} failed: {e}")
            import traceback
            traceback.print_exc()

    # Summary table
    print(f"\n\n{'='*70}")
    print(f"  SUMMARY")
    print(f"{'='*70}")
    print(f"\n  {'#':<4} {'Scenario':<35} {'Decision':<12} {'Escalated':<10} {'Time':<10}")
    print(f"  {'─'*4} {'─'*35} {'─'*12} {'─'*10} {'─'*10}")

    for r in all_results:
        sid = r["scenario_id"]
        title = r["meta"]["title"][:33]
        decision = r["consensus_decision"][:10]
        escalated = "Yes" if r["escalated"] else "No"
        elapsed = f"{r['elapsed']:.1f}s"
        print(f"  {sid:<4} {title:<35} {decision:<12} {escalated:<10} {elapsed:<10}")

    # Stats
    total = len(all_results)
    detect_count = sum(1 for r in all_results if r["consensus_decision"] == "detect")
    escalated_count = sum(1 for r in all_results if r["escalated"])

    print(f"\n  Total Scenarios: {total}")
    print(f"  Detection Rate: {detect_count}/{total} ({detect_count/total*100:.0f}%)")
    print(f"  Escalation Rate: {escalated_count}/{total} ({escalated_count/total*100:.0f}%)")
    print(f"{'='*70}\n")

    return all_results


if __name__ == "__main__":
    args = sys.argv[1:]

    if "--summary" in args:
        dashboard = ComplianceDashboard()
        print(dashboard.generate_summary_markdown())
    elif args:
        ids = [int(a) for a in args if a.isdigit()]
        run_all_scenarios(ids if ids else None)
    else:
        run_all_scenarios()
