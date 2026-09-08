"""
Dempster-Shafer Theory — Evidence Combination for Multi-Agent Consensus

Implements the Dempster-Shafer theory of evidence (also called
belief function theory) for combining evidence from multiple agents
with quantified uncertainty.

This is critical for compliance monitoring where:
- Agents may have partial knowledge
- Evidence quality varies across agents
- We need to quantify "don't know" separately from "believe" and "disbelieve"
"""

import math
from typing import Dict, List, Tuple
from dataclasses import dataclass


@dataclass
class MassAssignment:
    """Basic probability assignment for a hypothesis."""
    hypothesis: frozenset  # Set of possible states (e.g., frozenset({True, False}))
    mass: float           # Belief mass assigned to this hypothesis

    def __post_init__(self):
        if self.mass < 0 or self.mass > 1:
            raise ValueError(f"Mass must be between 0 and 1, got {self.mass}")


@dataclass
class BeliefFunction:
    """A complete belief function over a frame of discernment."""
    frame: frozenset  # The complete set of possible states
    masses: List[MassAssignment]

    def __post_init__(self):
        total = sum(m.mass for m in self.masses)
        if abs(total - 1.0) > 1e-10:
            raise ValueError(f"Masses must sum to 1.0, got {total}")

    def belief(self, subset: frozenset) -> float:
        """Calculate belief in a subset of the frame."""
        return sum(
            m.mass for m in self.masses
            if m.hypothesis.issubset(subset)
        )

    def plausibility(self, subset: frozenset) -> float:
        """Calculate plausibility of a subset (upper bound of probability)."""
        return sum(
            m.mass for m in self.masses
            if m.hypothesis.intersection(subset)
        )

    def uncertainty(self, subset: frozenset) -> float:
        """Calculate uncertainty (plausibility - belief)."""
        return self.plausibility(subset) - self.belief(subset)


def combine_evidence(
    bf1: BeliefFunction,
    bf2: BeliefFunction,
) -> BeliefFunction:
    """
    Dempster's rule of combination for two belief functions.

    Combines evidence from two independent sources while handling
    conflict between them via normalization.

    Args:
        bf1: First agent's belief function
        bf2: Second agent's belief function

    Returns:
        Combined belief function

    Raises:
        ValueError: If the frame of discernment doesn't match
    """
    if bf1.frame != bf2.frame:
        raise ValueError("Belief functions must share the same frame of discernment")

    frame = bf1.frame
    combined_masses: Dict[frozenset, float] = {}
    conflict_mass = 0.0

    for m1 in bf1.masses:
        for m2 in bf2.masses:
            intersection = m1.hypothesis.intersection(m2.hypothesis)
            product = m1.mass * m2.mass

            if not intersection:
                # Conflict — masses contradict each other
                conflict_mass += product
            else:
                if intersection not in combined_masses:
                    combined_masses[intersection] = 0.0
                combined_masses[intersection] += product

    # Normalization factor (1 - conflict)
    k = conflict_mass
    norm_factor = 1.0 - k

    if norm_factor < 1e-10:
        # Total conflict — evidence is completely contradictory
        # Distribute mass equally across all focal elements
        n = len(combined_masses)
        if n > 0:
            for hyp in combined_masses:
                combined_masses[hyp] = 1.0 / n
        else:
            # No focal elements — uniform distribution
            combined_masses[frame] = 1.0
    else:
        # Normalize
        for hyp in combined_masses:
            combined_masses[hyp] /= norm_factor

    masses = [MassAssignment(hypothesis=hyp, mass=mass) for hyp, mass in combined_masses.items()]

    return BeliefFunction(frame=frame, masses=masses)


def combine_multiple(
    belief_functions: List[BeliefFunction],
) -> BeliefFunction:
    """
    Combine multiple belief functions sequentially using Dempster's rule.

    Args:
        belief_functions: List of belief functions to combine

    Returns:
        Combined belief function
    """
    if not belief_functions:
        raise ValueError("Need at least one belief function to combine")

    result = belief_functions[0]
    for bf in belief_functions[1:]:
        result = combine_evidence(result, bf)

    return result


# ---------------------------------------------------------------------------
# Convenience: Create belief functions for compliance detection
# ---------------------------------------------------------------------------

def create_detection_belief(
    confidence: float,
    violation_detected: bool = True,
    frame: frozenset = frozenset({True, False}),
) -> BeliefFunction:
    """
    Create a belief function from an agent's detection confidence.

    Args:
        confidence: Agent's confidence (0.0 - 1.0)
        violation_detected: Whether the agent detected a violation
        frame: Frame of discernment ({True, False} for yes/no detection)

    Returns:
        Belief function representing the agent's assessment
    """
    detected = frozenset({True})
    not_detected = frozenset({False})
    both = frozenset({True, False})

    if violation_detected:
        # Agent believes violation occurred
        masses = [
            MassAssignment(hypothesis=detected, mass=confidence),
            MassAssignment(hypothesis=both, mass=1.0 - confidence),
        ]
    else:
        # Agent believes no violation
        masses = [
            MassAssignment(hypothesis=not_detected, mass=confidence),
            MassAssignment(hypothesis=both, mass=1.0 - confidence),
        ]

    return BeliefFunction(frame=frame, masses=masses)


def compute_consensus(
    agent_assessments: List[Dict[str, float]],
) -> Dict[str, float]:
    """
    Compute consensus from multiple agent assessments using Dempster-Shafer.

    Args:
        agent_assessments: List of {"confidence": float, "detected": bool}
                          from each agent

    Returns:
        {
            "belief_violation": float,    # Combined belief that violation occurred
            "belief_no_violation": float,  # Combined belief that no violation
            "plausibility_violation": float,
            "uncertainty": float,
            "conflict_level": str,         # low, medium, high
            "num_agents": int,
        }
    """
    frame = frozenset({True, False})

    belief_functions = [
        create_detection_belief(
            confidence=a["confidence"],
            violation_detected=a.get("detected", True),
            frame=frame,
        )
        for a in agent_assessments
    ]

    combined = combine_multiple(belief_functions) if belief_functions else None

    if combined is None:
        return {
            "belief_violation": 0.0,
            "belief_no_violation": 0.0,
            "plausibility_violation": 0.0,
            "uncertainty": 1.0,
            "conflict_level": "unknown",
            "num_agents": 0,
        }

    detected = frozenset({True})
    not_detected = frozenset({False})

    bv = combined.belief(detected)
    bnv = combined.belief(not_detected)
    pv = combined.plausibility(detected)
    unc = combined.uncertainty(detected)

    # Classify conflict level
    if unc < 0.2:
        conflict_level = "low"
    elif unc < 0.5:
        conflict_level = "medium"
    else:
        conflict_level = "high"

    return {
        "belief_violation": round(bv, 4),
        "belief_no_violation": round(bnv, 4),
        "plausibility_violation": round(pv, 4),
        "uncertainty": round(unc, 4),
        "conflict_level": conflict_level,
        "num_agents": len(agent_assessments),
    }
# D-S update
