"""
Conflict Taxonomy — Classification of Inter-Agent Disagreements

Categorizes the types of conflicts that can arise between agents
and provides resolution strategies for each type.

Conflict Types:
  Type A: Severity Disagreement — same violation, different severity level
  Type B: Existence Disagreement — one agent detects, another doesn't
  Type C: Jurisdictional Conflict — regulations from different jurisdictions conflict
  Type D: Temporal Conflict — regulation timing creates contradictory requirements
"""

from enum import Enum
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field


class ConflictType(str, Enum):
    SEVERITY_DISAGREEMENT = "severity_disagreement"
    EXISTENCE_DISAGREEMENT = "existence_disagreement"
    JURISDICTIONAL_CONFLICT = "jurisdictional_conflict"
    TEMPORAL_CONFLICT = "temporal_conflict"


class ConflictSeverity(str, Enum):
    LOW = "low"         # Minor disagreement, easily resolved
    MEDIUM = "medium"   # Notable disagreement, requires algorithmic resolution
    HIGH = "high"       # Significant disagreement, may need human input
    CRITICAL = "critical"  # Fundamental disagreement, must escalate


@dataclass
class ConflictInstance:
    """A specific conflict between agents."""
    conflict_id: str
    conflict_type: ConflictType
    severity: ConflictSeverity
    agents_involved: List[str]
    description: str
    details: Dict[str, Any] = field(default_factory=dict)
    resolution_strategy: str = ""
    resolved: bool = False
    resolution: Optional[Dict[str, Any]] = None


# ---------------------------------------------------------------------------
# Conflict Detection
# ---------------------------------------------------------------------------

def detect_conflicts(
    agent_assessments: Dict[str, Dict[str, Any]],
) -> List[ConflictInstance]:
    """
    Detect conflicts between agent assessments.

    Args:
        agent_assessments: {agent_id: {"detected": bool, "severity": str, "confidence": float, ...}}

    Returns:
        List of detected conflict instances
    """
    conflicts = []
    agents = list(agent_assessments.keys())

    # Type B: Existence Disagreement — some agents detect, others don't
    detecting = [a for a, d in agent_assessments.items() if d.get("detected", False)]
    not_detecting = [a for a, d in agent_assessments.items() if not d.get("detected", False)]

    if detecting and not_detecting:
        conflicts.append(ConflictInstance(
            conflict_id=f"CONFLICT-B-{len(conflicts)+1:03d}",
            conflict_type=ConflictType.EXISTENCE_DISAGREEMENT,
            severity=ConflictSeverity.HIGH if len(detecting) > 0 and len(not_detecting) > 0 else ConflictSeverity.MEDIUM,
            agents_involved=detecting + not_detecting,
            description=f"Existence disagreement: {detecting} detect violation, {not_detecting} do not",
            details={"detecting_agents": detecting, "non_detecting_agents": not_detecting},
            resolution_strategy="weighted_voting_with_confidence",
        ))

    # Type A: Severity Disagreement — same violation, different severity
    detecting_assessments = {a: d for a, d in agent_assessments.items() if d.get("detected", False)}
    severity_levels = {}
    for agent_id, data in detecting_assessments.items():
        sev = data.get("severity", "MEDIUM")
        severity_levels.setdefault(sev, []).append(agent_id)

    if len(severity_levels) > 1:
        max_sev = max(severity_levels.keys())
        min_sev = min(severity_levels.keys())
        sev_diff = ["CRITICAL", "HIGH", "MEDIUM", "LOW"].index(max_sev) - \
                   ["CRITICAL", "HIGH", "MEDIUM", "LOW"].index(min_sev)

        if sev_diff >= 2:
            conflicts.append(ConflictInstance(
                conflict_id=f"CONFLICT-A-{len(conflicts)+1:03d}",
                conflict_type=ConflictType.SEVERITY_DISAGREEMENT,
                severity=ConflictSeverity.HIGH,
                agents_involved=sum(severity_levels.values(), []),
                description=f"Severity disagreement: range from {min_sev} to {max_sev}",
                details={"severity_distribution": {k: v for k, v in severity_levels.items()}},
                resolution_strategy="highest_authority_precedence",
            ))
        elif sev_diff == 1:
            conflicts.append(ConflictInstance(
                conflict_id=f"CONFLICT-A-{len(conflicts)+1:03d}",
                conflict_type=ConflictType.SEVERITY_DISAGREEMENT,
                severity=ConflictSeverity.MEDIUM,
                agents_involved=sum(severity_levels.values(), []),
                description=f"Minor severity disagreement: {min_sev} vs {max_sev}",
                details={"severity_distribution": {k: v for k, v in severity_levels.items()}},
                resolution_strategy="weighted_average",
            ))

    return conflicts


# ---------------------------------------------------------------------------
# Conflict Resolution Strategies
# ---------------------------------------------------------------------------

def resolve_by_weighted_voting(
    agent_assessments: Dict[str, Dict[str, Any]],
    agent_weights: Optional[Dict[str, float]] = None,
) -> Dict[str, Any]:
    """
    Resolve conflicts using weighted voting based on agent confidence.

    Default weights: TM=0.3, CS=0.3, RU=0.25, RG=0.15
    (Transaction Monitor and Communication Scanner have highest authority
     for detection events)
    """
    default_weights = {
        "TM-001": 0.30,
        "CS-001": 0.30,
        "RU-001": 0.25,
        "RG-001": 0.15,
    }
    weights = agent_weights or default_weights

    weighted_votes = {"detect": 0.0, "no_detect": 0.0}
    for agent_id, data in agent_assessments.items():
        w = weights.get(agent_id, 0.1)
        conf = data.get("confidence", 0.5)
        weighted = w * conf

        if data.get("detected", False):
            weighted_votes["detect"] += weighted
        else:
            weighted_votes["no_detect"] += weighted

    total = sum(weighted_votes.values())
    if total > 0:
        detect_prob = weighted_votes["detect"] / total
    else:
        detect_prob = 0.5

    return {
        "decision": "detect" if detect_prob > 0.5 else "no_detect",
        "confidence": round(detect_prob, 4),
        "weighted_votes": weighted_votes,
        "method": "weighted_voting",
    }


def resolve_severity_by_highest_authority(
    agent_assessments: Dict[str, Dict[str, Any]],
    authority_order: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """
    When agents disagree on severity, the highest-authority agent's
    assessment prevails. Authority order: TM > CS > RU > RG for detection severity.
    """
    default_order = ["TM-001", "CS-001", "RU-001", "RG-001"]
    order = authority_order or default_order

    sev_rank = {"CRITICAL": 4, "HIGH": 3, "MEDIUM": 2, "LOW": 1}

    best_agent = None
    best_severity = 0
    for agent_id in order:
        if agent_id in agent_assessments:
            data = agent_assessments[agent_id]
            if data.get("detected", False):
                sev = sev_rank.get(data.get("severity", "MEDIUM"), 0)
                if sev > best_severity:
                    best_severity = sev
                    best_agent = agent_id

    if best_agent:
        rank_to_name = {4: "CRITICAL", 3: "HIGH", 2: "MEDIUM", 1: "LOW"}
        return {
            "decision": rank_to_name.get(best_severity, "MEDIUM"),
            "deciding_agent": best_agent,
            "method": "highest_authority_precedence",
        }

    return {"decision": "MEDIUM", "deciding_agent": None, "method": "default"}


# ---------------------------------------------------------------------------
# Main Conflict Resolver
# ---------------------------------------------------------------------------

class ConflictResolver:
    """Orchestrates conflict detection and resolution."""

    def __init__(self):
        self._conflicts: List[ConflictInstance] = []

    def resolve(
        self,
        agent_assessments: Dict[str, Dict[str, Any]],
        trace_id: str = "",
    ) -> Dict[str, Any]:
        """
        Detect and resolve all conflicts in agent assessments.

        Returns comprehensive resolution result.
        """
        # Detect conflicts
        conflicts = detect_conflicts(agent_assessments)
        self._conflicts.extend(conflicts)

        if not conflicts:
            # No conflicts — agents agree
            consensus = resolve_by_weighted_voting(agent_assessments)
            return {
                "has_conflicts": False,
                "consensus": consensus,
                "conflicts": [],
                "resolution_applied": None,
            }

        # Resolve each conflict type
        resolutions = []
        for conflict in conflicts:
            if conflict.conflict_type == ConflictType.EXISTENCE_DISAGREEMENT:
                resolution = resolve_by_weighted_voting(agent_assessments)
            elif conflict.conflict_type == ConflictType.SEVERITY_DISAGREEMENT:
                resolution = resolve_severity_by_highest_authority(agent_assessments)
            else:
                resolution = resolve_by_weighted_voting(agent_assessments)

            conflict.resolved = True
            conflict.resolution = resolution
            resolutions.append({
                "conflict_id": conflict.conflict_id,
                "type": conflict.conflict_type.value,
                "severity": conflict.severity.value,
                "resolution": resolution,
            })

        # Final consensus after resolution
        consensus = resolve_by_weighted_voting(agent_assessments)

        return {
            "has_conflicts": True,
            "consensus": consensus,
            "conflicts": [
                {
                    "id": c.conflict_id,
                    "type": c.conflict_type.value,
                    "severity": c.severity.value,
                    "agents": c.agents_involved,
                    "description": c.description,
                }
                for c in conflicts
            ],
            "resolutions": resolutions,
            "resolution_applied": resolutions[0] if resolutions else None,
        }

    def get_conflict_history(self) -> List[ConflictInstance]:
        return self._conflicts
# Conflict update
