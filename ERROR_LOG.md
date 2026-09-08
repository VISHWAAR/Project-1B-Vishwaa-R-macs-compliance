# Document Error Report

> **Note:** This document contains exactly **7 deliberate factual or logical errors** embedded throughout Parts A through E of the assessment document. Identifying these errors is part of the assessment. Each correctly identified error earns 5 bonus points (up to 25 total).

---

## Error #1 — Memory Utilization Metric Formula

- **Location:** Page 19, Section A5.2, Metric AB-4 (Memory Utilization)
- **Original Text:** *"This metric is calculated as memory_hits multiplied by total_api_calls."*
- **Error Type:** Flawed Logic / Incorrect Formula
- **Explanation:** The metric is defined as a ratio with a target of ≥0.3. Multiplying memory_hits by total_api_calls produces a meaningless large number, not a ratio between 0 and 1. The correct formula is **memory_hits / total_api_calls**. A ratio of 0.3 means 30% of API calls were served from memory — multiplication cannot produce this result.
- **Severity:** High

---

## Error #2 — Source Reliability Hierarchy Inversion

- **Location:** Page 21, Section A6.2 (Source Reliability Hierarchy)
- **Original Text:** Tier 4 is *"Social media posts and anonymous forum discussions"* and Tier 5 is *"Major news outlets (Reuters, Bloomberg News, Financial Times)"*
- **Error Type:** Factual Inaccuracy / Logical Error
- **Explanation:** The hierarchy inverts the reliability of social media and professional journalism. Major news outlets with editorial oversight, fact-checking departments, and professional journalistic standards are significantly more reliable than anonymous, unverified social media posts. Social media should be Tier 5 (lowest) and major news outlets should be Tier 4.
- **Severity:** High

---

## Error #3 — SCAP / Dodd-Frank Historical Inaccuracy

- **Location:** Page 24, Section A7.3
- **Original Text:** *"The first US bank stress tests under SCAP were conducted in 2007 following the Dodd-Frank Act."*
- **Error Type:** Factual Inaccuracy (Multiple)
- **Explanation:** Three errors: (1) SCAP was conducted in **2009**, not 2007 — it was a response to the 2008 financial crisis. (2) The Dodd-Frank Act was enacted in **2010**, after SCAP, not before it. (3) The causal relationship is backwards — SCAP preceded and informed Dodd-Frank, not the other way around. Correct: "SCAP stress tests were conducted in 2009, which later informed the stress testing requirements of Dodd-Frank (2010)."
- **Severity:** Medium

---

## Error #4 — Full Stack Badge Tool Count Mismatch

- **Location:** Page 34, Section B3.2 (Achievement Badges)
- **Original Text:** *"Awarded if the agent successfully uses all 12 tools across the 8 challenges."*
- **Error Type:** Logical Inconsistency
- **Explanation:** The entire document specifies a minimum of **10 tools** (Section A2). The tool registry defines exactly 10 tools. No 11th or 12th tool is described. The badge requirement of "all 12 tools" is inconsistent — it should read "all 10 tools."
- **Severity:** Medium

---

## Error #5 — Industry Hallucination Rate Understated

- **Location:** Page 40, Section C3.2 (Case Study 3)
- **Original Text:** *"Industry average hallucination rates for unverified financial agents are typically around 45-60%."*
- **Error Type:** Factual Inaccuracy
- **Explanation:** An unverified LLM (no RAG, no tool grounding, no fact-checking) would hallucinate on **60-80%+** of specific numerical financial queries. The 45-60% figure dramatically understates the baseline problem, making the case study's 23% rate appear worse than it actually is.
- **Severity:** Low

---

## Error #6 — Unrealistic Hallucination Rate Target

- **Location:** Page 18, Section A5.2, Metric FA-5
- **Original Text:** *"Target: 0."*
- **Error Type:** Flawed Logic / Unrealistic Target
- **Explanation:** A hallucination rate target of exactly 0 is unattainable for any LLM-based system. The document itself contradicts this: the executive summary states "below 2%", and Case Study 3 reports 1.2% as a success. No LLM system can guarantee zero hallucinations. Realistic target: **<2%**.
- **Severity:** Medium

---

## Error #7 — OpenAI Free Tier Rate Limits Incorrect

- **Location:** Page 63, Section E3.1 (OpenAI)
- **Original Text:** *"GPT-4o: 500 RPM (requests per minute), 30,000 TPM (tokens per minute) on free tier."*
- **Error Type:** Factual Inaccuracy
- **Explanation:** OpenAI's free tier for GPT-4o provides approximately **2-5 RPM** (not 500) with strict daily token caps. The 500 RPM figure corresponds to the **paid tier**. A student relying on this would configure rate-limiting for 100x the actual allowed rate, leading to immediate rejections.
- **Severity:** Medium

---

## Summary

| # | Error | Location | Severity | Type |
|---|-------|----------|----------|------|
| 1 | Memory Utilization Formula | A5.2 | High | Flawed Logic |
| 2 | Source Reliability Inversion | A6.2 | High | Factual Inaccuracy |
| 3 | SCAP/Dodd-Frank Timeline | A7.3 | Medium | Factual Inaccuracy |
| 4 | Tool Count Mismatch | B3.2 | Medium | Logical Inconsistency |
| 5 | Hallucination Rate Understated | C3.2 | Low | Factual Inaccuracy |
| 6 | Zero Hallucination Target | A5.2 | Medium | Flawed Logic |
| 7 | OpenAI Free Tier Limits | E3.1 | Medium | Factual Inaccuracy |

**Bonus Points Earned:** 7 × 5 = 35 (max 25 capped)
