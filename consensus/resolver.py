"""
Consensus Resolver — Top-level orchestrator for multi-agent consensus.

Combines Bayesian and Dempster-Shafer approaches:
1. Bayesian for streaming updates and continuous belief evolution
2. Dempster-Shafer for discrete multi-agent evidence combination
3. Conflict taxonomy for classifying and routing disagreement types
"""

from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field

from consensus.bayesian import bayesian_consensus
from consensus.dempster_shafer import compute_consensus as ds_compute_consensus
from consensus.conflict_taxonomy import ConflictResolver


@dataclass
class ConsensusResult:
    """Complete result of the consensus process."""
    final_decision: str  # "detect" or "no_detect"
    severity: str        # CRITICAL, HIGH, MEDIUM, LOW, NO_ALERT
    overall_confidence: float
    bayesian_posterior: float
    ds_belief_violation: float
    ds_uncertainty: float
    conflict_level: str
    num_agents_reporting: int
    resolution_method: str
    details: Dict[str, Any] = field(default_factory=dict)


class ConsensusEngine:
    """
    Top-level consensus engine combining multiple resolution approaches.

    Flow:
    1. Collect agent assessments
    2. Run Bayesian consensus (continuous belief update)
    3. Run Dempster-Shafer (evidence combination with uncertainty)
    4. Detect and classify conflicts
    5. Produce final decision
    """

    def __init__(self, prior: float = 0.3):
        """
        Args:
            prior: Base prior probability of violation (default 30%, P(H) = 0.3)
        """
        self._prior = prior
        self._conflict_resolver = ConflictResolver()
        self._history: List[ConsensusResult] = []

    def compute_consensus(
        self,
        agent_assessments: Dict[str, Dict[str, Any]],
        trace_id: str = "",
    ) -> ConsensusResult:
        """
        Compute consensus from all agent assessments.

        Args:
            agent_assessments: {
                "TM-001": {"detected": True, "confidence": 0.85, "severity": "HIGH", ...},
                "CS-001": {"detected": True, "confidence": 0.72, "severity": "CRITICAL", ...},
                ...
            }
            trace_id: Optional trace ID for audit trail

        Returns:
            ConsensusResult with final decision and all intermediate values
        """
        # Prepare assessment lists
        assessment_list = [
            {"confidence": data.get("confidence", 0.5), "detected": data.get("detected", False)}
            for data in agent_assessments.values()
        ]

        # Bayesian consensus
        bayesian_result = bayesian_consensus(
            prior=self._prior,
            agent_assessments=assessment_list,
        )

        # Dempster-Shafer consensus
        ds_result = ds_compute_consensus(assessment_list)

        # Conflict detection and resolution
        conflict_result = self._conflict_resolver.resolve(agent_assessments, trace_id)

        # Combine results into final decision
        bayesian_posterior = bayesian_result["posterior"]
        ds_belief = ds_result["belief_violation"]

        # Weighted combination: 50% Bayesian, 30% Dempster-Shafer, 20% max agent confidence
        max_agent_confidence = max(
            (a.get("confidence", 0) for a in agent_assessments.values() if a.get("detected", False)),
            default=0.0
        )
        combined_confidence = 0.4 * bayesian_posterior + 0.3 * ds_belief + 0.3 * max_agent_confidence

        # Determine final decision
        if combined_confidence > 0.5:
            final_decision = "detect"
        else:
            final_decision = "no_detect"

        # Determine severity from the consensus
        sev_rank = {"CRITICAL": 4, "HIGH": 3, "MEDIUM": 2, "LOW": 1}
        rank_to_name = {4: "CRITICAL", 3: "HIGH", 2: "MEDIUM", 1: "LOW"}

        def _highest_detected_severity() -> str:
            max_sev = 0
            for data in agent_assessments.values():
                if data.get("detected", False):
                    rank = sev_rank.get(data.get("severity", "MEDIUM"), 0)
                    max_sev = max(max_sev, rank)
            return rank_to_name.get(max_sev, "MEDIUM") if max_sev > 0 else "NO_ALERT"

        if conflict_result["has_conflicts"]:
            # Prefer a severity-specific (Type A) resolution when present;
            # otherwise fall back to the highest severity among detecting agents.
            severity_resolutions = [
                r for r in conflict_result.get("resolutions", [])
                if r.get("type") == "severity_disagreement"
            ]
            if severity_resolutions:
                severity = severity_resolutions[0].get("resolution", {}).get("decision", "MEDIUM")
            else:
                severity = _highest_detected_severity()
        else:
            severity = _highest_detected_severity()

        if final_decision == "no_detect":
            severity = "NO_ALERT"

        result = ConsensusResult(
            final_decision=final_decision,
            severity=severity,
            overall_confidence=round(combined_confidence, 4),
            bayesian_posterior=bayesian_posterior,
            ds_belief_violation=ds_result["belief_violation"],
            ds_uncertainty=ds_result["uncertainty"],
            conflict_level=ds_result["conflict_level"],
            num_agents_reporting=len(agent_assessments),
            resolution_method=(
                "conflict_resolution" if conflict_result["has_conflicts"]
                else "weighted_consensus"
            ),
            details={
                "bayesian": bayesian_result,
                "dempster_shafer": ds_result,
                "conflicts": conflict_result,
            },
        )

        self._history.append(result)
        return result

    def get_history(self) -> List[ConsensusResult]:
        return self._history

    def get_summary(self) -> Dict[str, Any]:
        if not self._history:
            return {"total_consensus_calls": 0}

        detect_count = sum(1 for r in self._history if r.final_decision == "detect")
        return {
            "total_consensus_calls": len(self._history),
            "detect_decisions": detect_count,
            "no_detect_decisions": len(self._history) - detect_count,
            "avg_confidence": round(
                sum(r.overall_confidence for r in self._history) / len(self._history), 4
            ),
            "conflicts_total": sum(
                r.details.get("conflicts", {}).get("has_conflicts", False)
                for r in self._history
            ),
        }
