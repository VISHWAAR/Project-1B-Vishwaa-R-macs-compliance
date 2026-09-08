"""
Bayesian Consensus — Updating Shared Beliefs via Bayesian Inference

Agents update shared beliefs using Bayesian inference, converging
on a posterior probability for violation detection.

Each agent contributes a likelihood ratio based on its detection
confidence, and the system maintains a prior that evolves over time
as more evidence accumulates.
"""

import math
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field


@dataclass
class BayesianBelief:
    """A Bayesian belief state about a hypothesis."""
    prior_prob: float           # Prior probability of hypothesis being true
    evidence_history: List[Dict[str, float]] = field(default_factory=list)
    posterior_prob: float = 0.0

    def __post_init__(self):
        if not self.evidence_history:
            self.posterior_prob = self.prior_prob

    def update(self, likelihood_ratio: float, source_confidence: float = 1.0):
        """
        Update belief with new evidence using Bayes' theorem.

        Args:
            likelihood_ratio: P(evidence | H) / P(evidence | ~H)
                             Values > 1 support the hypothesis
                             Values < 1 contradict it
            source_confidence: Confidence in the source (0-1), weights the update
        """
        # Adjust the likelihood ratio by source confidence
        # A less confident source contributes less evidence
        adjusted_lr = 1.0 + (likelihood_ratio - 1.0) * source_confidence

        # Bayes' theorem: P(H|E) = P(E|H) * P(H) / P(E)
        # Using odds form: odds(H|E) = LR * odds(H)
        # Sequential update: the current posterior becomes the prior for
        # the next piece of evidence, so the belief evolves over time.
        current_prob = self.posterior_prob if self.evidence_history else self.prior_prob
        prior_odds = current_prob / (1.0 - current_prob + 1e-10)
        posterior_odds = adjusted_lr * prior_odds
        self.posterior_prob = posterior_odds / (1.0 + posterior_odds)
        self.posterior_prob = max(0.001, min(0.999, self.posterior_prob))

        self.evidence_history.append({
            "likelihood_ratio": likelihood_ratio,
            "source_confidence": source_confidence,
            "adjusted_lr": adjusted_lr,
            "posterior_after": self.posterior_prob,
        })

    def get_confidence_interval(self, width: float = 0.05) -> Tuple[float, float]:
        """Get a simple confidence interval around the posterior."""
        half_width = width * math.sqrt(
            self.posterior_prob * (1 - self.posterior_prob) / max(len(self.evidence_history), 1)
        )
        return (
            max(0.0, self.posterior_prob - half_width),
            min(1.0, self.posterior_prob + half_width),
        )


def confidence_to_likelihood_ratio(confidence: float, detected: bool) -> float:
    """
    Convert an agent's detection confidence to a Bayesian likelihood ratio.

    Args:
        confidence: Agent's confidence (0-1)
        detected: Whether the agent detected a violation

    Returns:
        Likelihood ratio > 1 supports violation, < 1 contradicts
    """
    # Map confidence to likelihood ratio
    # confidence = 0.5 → LR = 1.0 (no evidence)
    # confidence = 1.0, detected → LR = high (strong evidence for)
    # confidence = 1.0, not detected → LR = low (strong evidence against)
    if detected:
        return 1.0 + confidence * 9.0  # LR range: 1.0 to 10.0
    else:
        return 1.0 / (1.0 + confidence * 9.0)  # LR range: 1.0 to 0.111


def bayesian_consensus(
    prior: float,
    agent_assessments: List[Dict[str, float]],
    decay_factor: float = 0.95,
) -> Dict[str, float]:
    """
    Compute Bayesian consensus from multiple agent assessments.

    Args:
        prior: Prior probability of violation (0-1)
        agent_assessments: List of {"confidence": float, "detected": bool}
        decay_factor: How much to weight older evidence (for streaming updates)

    Returns:
        {
            "posterior": float,
            "prior": float,
            "num_updates": int,
            "confidence_interval": (float, float),
            "evidence_strength": str,  # weak, moderate, strong, conclusive
            "recommendation": str,
        }
    """
    belief = BayesianBelief(prior_prob=prior)

    for assessment in agent_assessments:
        confidence = assessment.get("confidence", 0.5)
        detected = assessment.get("detected", True)
        lr = confidence_to_likelihood_ratio(confidence, detected)
        belief.update(lr, source_confidence=confidence)

    ci = belief.get_confidence_interval()

    # Classify evidence strength
    n = len(belief.evidence_history)
    spread = ci[1] - ci[0]
    if n < 2:
        evidence_strength = "weak"
    elif spread < 0.1:
        evidence_strength = "conclusive"
    elif spread < 0.2:
        evidence_strength = "strong"
    else:
        evidence_strength = "moderate"

    # Generate recommendation
    if belief.posterior_prob > 0.8:
        recommendation = "ESCALATE — Strong evidence of violation"
    elif belief.posterior_prob > 0.5:
        recommendation = "INVESTIGATE — Moderate evidence, further analysis needed"
    elif belief.posterior_prob > 0.2:
        recommendation = "MONITOR — Weak evidence, continue surveillance"
    else:
        recommendation = "NO_ACTION — Insufficient evidence of violation"

    return {
        "posterior": round(belief.posterior_prob, 4),
        "prior": prior,
        "num_updates": len(belief.evidence_history),
        "confidence_interval": (round(ci[0], 4), round(ci[1], 4)),
        "evidence_strength": evidence_strength,
        "recommendation": recommendation,
    }
