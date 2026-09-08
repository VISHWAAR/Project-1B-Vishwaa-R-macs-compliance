# Conflict Taxonomy

## Overview

In a multi-agent compliance monitoring system, agents may disagree on their assessments. One agent may detect a violation with high confidence while another finds nothing. They may agree a violation occurred but disagree on severity. They may operate under conflicting regulatory requirements from different jurisdictions.

The Conflict Taxonomy classifies these disagreement types and defines how each is resolved. The classification is implemented in `consensus/conflict_taxonomy.py` via the `ConflictResolver` class.

## Why Conflict Resolution Matters

In compliance monitoring, false negatives (missing a real violation) are typically more costly than false positives (flagging legitimate activity for human review). Conflict resolution is therefore biased toward **conservative** outcomes — when agents disagree, the system errs on the side of flagging for human review rather than silently dismissing.

## Conflict Types

### Type A: Severity Disagreement

**Definition:** Two or more agents agree that a violation of a particular type occurred, but they assign different severity levels.

**Example:**
- TM-001 detects insider trading, assigns CRITICAL severity (pre-announcement accumulation with 35% price jump)
- CS-001 detects communication link, assigns HIGH severity (keyword match on "private dinner")
- Both agree: insider trading. They disagree: is it CRITICAL or HIGH?

**Detection criteria:**
```python
# In ConflictResolver.resolve()
# Agents with same violation_type but different severity values
severity_groups = group_by_violation_type(agent_assessments)
for vtype, agents in severity_groups.items():
    severities = {a["severity"] for a in agents if a["detected"]}
    if len(severities) > 1:
        # Type A conflict
```

**Resolution:** Highest severity among detecting agents wins. This is conservative — if any agent thinks it's CRITICAL, the system treats it as CRITICAL.

```
severity_rank = {"CRITICAL": 4, "HIGH": 3, "MEDIUM": 2, "LOW": 1}
resolution = max(severities, key=lambda s: severity_rank[s])
```

**Rationale:** In compliance, under-classification is riskier than over-classification. A CRITICAL violation treated as HIGH could result in missed regulatory filing deadlines. A HIGH violation treated as CRITICAL results in extra human review — annoying but safe.

---

### Type B: Detection Disagreement

**Definition:** Some agents detect a violation while others do not. This is the most common conflict type and the most important to resolve correctly.

**Example:**
- TM-001 detects spoofing: confidence 0.85, "92% cancel rate, 47 cancelled large orders"
- CS-001 detects nothing: confidence 0.3, "No communication violations detected"
- RU-001 detects nothing: confidence 0.3, "No regulatory updates requiring action"

This is CS-02 (Spoofing). TM says "detect", CS and RU say "no_detect".

**Detection criteria:**
```python
# In ConflictResolver.resolve()
detecting = [a for a in agent_assessments.values() if a.get("detected")]
non_detecting = [a for a in agent_assessments.values() if not a.get("detected")]
if detecting and non_detecting:
    # Type B conflict
```

**Resolution:** Bayesian posterior governs. The consensus engine computes a posterior probability of violation given all agent assessments (using prior P(H) = 0.3 and likelihood ratios from each agent). If posterior > 0.5, the final decision is "detect", otherwise "no_detect".

**Why Bayesian for this type:**
- Detection disagreement is fundamentally a statistical question: "Given that agent A says yes with confidence X and agent B says no with confidence Y, what's the probability a violation occurred?"
- Bayesian updating handles this naturally — each agent's assessment is a likelihood ratio that updates the prior
- Dempster-Shafer is complementary — it handles uncertainty quantification and conflict between evidence sources

**Weighted combination in ConsensusEngine:**
```python
combined_confidence = (0.4 * bayesian_posterior +
                       0.3 * ds_belief_violation +
                       0.3 * max_agent_confidence)
final_decision = "detect" if combined_confidence > 0.5 else "no_detect"
```

The final decision blends Bayesian (40%), Dempster-Shafer (30%), and max agent confidence (30%). This ensures that even if Bayesian and D-S disagree, a single high-confidence agent can still drive a detection — appropriate for compliance where one credible detection should trigger review.

---

### Type C: Jurisdictional Conflict

**Definition:** The Regulatory Tracker detects that regulations from two different jurisdictions impose contradictory or incompatible requirements on the same activity.

**Example:**
- RU-001 detects that EU GDPR requires data localization for personal data
- RU-001 also detects that a US regulation requires cross-border data sharing for anti-money laundering
- These two requirements conflict for an entity operating in both jurisdictions

**Detection criteria:**
```python
# In ConflictResolver.resolve()
# RU agent reports jurisdictional_conflict in its assessment
for agent_id, assessment in agent_assessments.items():
    if agent_id == "RU-001" and assessment.get("violation_type") == "REGULATORY_CHANGE":
        if assessment.get("jurisdictions", []) and len(assessment["jurisdictions"]) > 1:
            # Potential Type C conflict
```

**Resolution:** RU jurisdiction recommendation prevails. The RU agent's assessment of which jurisdiction takes precedence (based on regulatory hierarchy, entity domicile, and activity location) is used as the resolution. However, this is flagged for human legal review — the system does not make final legal determinations.

```
resolution: "jurisdiction_a_precedence" | "jurisdiction_b_precedence" | "human_review_required"
```

**Rationale:** Cross-jurisdictional conflicts are legal questions that require human expertise. The system identifies the conflict, surfaces both sides, and recommends based on RU analysis, but escalates to human legal review for final determination.

---

## Conflict Resolution Flow

```
┌─────────────────────────────────────────────────────────────┐
│              Conflict Resolution Pipeline                    │
│                                                             │
│  Agent assessments collected → ConflictResolver.resolve()   │
│                                                             │
│  ┌───────────────────────────────────────────────────────┐ │
│  │ Step 1: Group agents by violation type                │ │
│  │   - TM-001: INSIDER_TRADING, CRITICAL                │ │
│  │   - CS-001: INSIDER_TRADING, HIGH                   │ │
│  │   - RU-001: none                                    │ │
│  └───────────────────────────────────────────────────────┘ │
│                          ▼                                  │
│  ┌───────────────────────────────────────────────────────┐ │
│  │ Step 2: Classify each group                           │ │
│  │                                                       │ │
│  │  INSIDER_TRADING group:                              │ │
│  │    - Multiple severities → Type A                    │ │
│  │    - Detecting + non-detecting → Type B             │ │
│  └───────────────────────────────────────────────────────┘ │
│                          ▼                                  │
│  ┌───────────────────────────────────────────────────────┐ │
│  │ Step 3: Resolve each type                             │ │
│  │                                                       │ │
│  │  Type A → highest severity wins                      │ │
│  │  Type B → Bayesian posterior governs                 │ │
│  │  Type C → RU precedence + human review flag         │ │
│  └───────────────────────────────────────────────────────┘ │
│                          ▼                                  │
│  ┌───────────────────────────────────────────────────────┐ │
│  │ Step 4: Produce resolution record                     │ │
│  │  - type: "severity_disagreement" | "detection_        │ │
│  │          disagreement" | "jurisdictional_conflict"   │ │
│  │  - agents_involved: [...]                            │ │
│  │  - resolution: {decision, rationale, confidence}     │ │
│  │  - escalation_recommended: bool                      │ │
│  └───────────────────────────────────────────────────────┘ │
│                                                             │
│  Output: ConflictResolutionResult (merged into Consensus    │
│  Result.details["conflicts"])                                │
└─────────────────────────────────────────────────────────────┘
```

## Severity Ranking

```
CRITICAL (4) > HIGH (3) > MEDIUM (2) > LOW (1) > NO_ALERT (0)
```

When multiple agents assign different severities and there is no conflict resolution override, the highest severity is used. This is a deliberate conservative design choice.

## Integration with Consensus Engine

The `ConsensusEngine.compute_consensus()` method integrates conflict resolution:

```python
# consensus/resolver.py — ConsensusEngine.compute_consensus()

# ... run Bayesian and D-S ...

# Conflict detection and resolution
conflict_result = self._conflict_resolver.resolve(agent_assessments, trace_id)

# If conflicts exist, use conflict resolution severity
if conflict_result["has_conflicts"]:
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

# If consensus says no_detect, override severity to NO_ALERT
if final_decision == "no_detect":
    severity = "NO_ALERT"
```

## Escalation Trigger from Conflicts

Conflicts can themselves trigger escalation:

```python
# escalation/framework.py — evaluate_triggers()
if detecting > 0 and not_detecting > 0:
    triggered.append(EscalationTrigger.MULTI_AGENT_CONFLICT)
```

A multi-agent conflict (Type B detection disagreement) triggers escalation if there are at least 2 agents with conflicting assessments.

## Scenario Coverage

| Scenario | Conflict Type | Agents in Conflict | Resolution |
|----------|--------------|-------------------|------------|
| CS-01 (Insider Trading) | Type A (severity) | TM: CRITICAL, CS: HIGH | Highest severity → CRITICAL |
| CS-02 (Spoofing) | Type B (detection) | TM: detect, CS: no_detect | Bayesian posterior → detect |
| CS-05 (Chinese Wall) | None (single agent) | CS only | N/A |
| CS-07 (Regulatory Change) | None (single agent) | RU only | N/A |
| CS-09 (Sanctions) | Type B (detection) | TM: partial, RU: confirm | Both agree → detect |
| CS-19 (Multi-Jurisdiction) | Type C (jurisdictional) | RU: conflict between jurisdictions | RU precedence + human review |
| CS-20 (Coordinated AML) | Type A + Type B | TM: detect, CS: detect, RU: detect, all agree | Consensus → detect, Tier 4 escalation |

CS-18 (False Positive) is not a conflict scenario — it's a single-agent (TM) detection that is correctly cleared by the false positive verification path.

## Implementation

See `consensus/conflict_taxonomy.py`:
- `ConflictResolver` — classifies and resolves agent conflicts
- `ConflictType` enum — A, B, C
- `ConflictResolution` dataclass — resolution record
- `ConflictResolutionResult` — collection of resolutions

See `consensus/resolver.py`:
- `ConsensusEngine.compute_consensus()` — integrates conflict resolution into consensus pipeline
