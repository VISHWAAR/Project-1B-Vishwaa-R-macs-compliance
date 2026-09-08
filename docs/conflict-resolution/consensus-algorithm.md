# Consensus Algorithm — Formal Specification

**Version:** 1.0.0

---

## 1. Overview

The consensus algorithm combines three approaches to resolve inter-agent disagreements:

1. **Bayesian Consensus** — continuous belief updating
2. **Dempster-Shafer Theory** — evidence combination with uncertainty
3. **Conflict Taxonomy** — classification and routing of disagreements

## 2. Bayesian Consensus

### 2.1 Prior
Base prior probability of violation: P(H) = 0.3 (30%)

### 2.2 Likelihood Ratio Conversion
Each agent's assessment is converted to a likelihood ratio:

```
If detected:
  LR = 1 + confidence × 9    (range: 1.0 to 10.0)

If not detected:
  LR = 1 / (1 + confidence × 9)  (range: 1.0 to 0.111)
```

### 2.3 Bayesian Update
Using odds form of Bayes' theorem:

```
odds(H|E) = LR × odds(H)
P(H|E) = odds(H|E) / (1 + odds(H|E))
```

### 2.4 Evidence Strength Classification

| Confidence Interval Width | Strength |
|--------------------------|----------|
| n < 2 updates | Weak |
| spread ≥ 0.2 | Moderate |
| 0.1 ≤ spread < 0.2 | Strong |
| spread < 0.1 | Conclusive |

### 2.5 Decision Thresholds

| Posterior | Recommendation |
|-----------|---------------|
| > 0.8 | ESCALATE — Strong evidence |
| > 0.5 | INVESTIGATE — Moderate evidence |
| > 0.2 | MONITOR — Weak evidence |
| ≤ 0.2 | NO_ACTION — Insufficient evidence |

## 3. Dempster-Shafer Evidence Combination

### 3.1 Frame of Discernment
Θ = {True, False}  (violation detected vs. not detected)

### 3.2 Basic Probability Assignment (BPA)
Each agent provides masses:
- m({True}) = confidence (if detected)
- m({False}) = confidence (if not detected)
- m({True, False}) = 1 - confidence (uncertainty)

### 3.3 Dempster's Rule of Combination
For two belief functions m₁ and m₂:

```
m_combined(A) = Σ m₁(B) × m₂(C) / (1 - k)    where B ∩ C = A
k = Σ m₁(B) × m₂(C)                            where B ∩ C = ∅
```

### 3.4 Consensus Output
- **Belief Violation**: Combined belief that violation occurred
- **Plausibility Violation**: Upper bound on probability
- **Uncertainty**: Plausibility - Belief (gap represents "don't know")
- **Conflict Level**: low (<0.2), medium (0.2-0.5), high (>0.5)

## 4. Final Decision

Combined confidence = 0.4 × Bayesian_posterior + 0.3 × DS_belief + 0.3 × max_agent_confidence

| Combined Confidence | Decision |
|--------------------|----------| 
| > 0.5 | DETECT |
| ≤ 0.5 | NO_DETECT |

## 5. Conflict Taxonomy

| Type | Description | Resolution Strategy |
|------|-------------|-------------------|
| A: Severity | Same violation, different severity | Highest authority precedence (TM > CS > RU > RG) |
| B: Existence | One detects, another doesn't | Weighted voting with confidence |
| C: Jurisdictional | Regulations from different jurisdictions conflict | Escalate to Tier 3+ for human review |
| D: Temporal | Regulation timing creates contradictions | Escalate to Tier 2+ with timeline analysis |
