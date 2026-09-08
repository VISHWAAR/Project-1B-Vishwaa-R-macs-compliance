# Scenario Summary — All 20 Compliance Scenarios

| # | Scenario | Agents | Complexity | Expected | Actual Decision | Escalation | Status |
|---|----------|--------|------------|----------|----------------|------------|--------|
| CS-01 | Insider Trading | TM+CS | High | CRITICAL | detect | Tier 3 | ✅ PASS |
| CS-02 | Spoofing | TM | Medium | HIGH | detect | Tier 2 | ✅ PASS |
| CS-03 | Unsuitable Recommendation | CS+TM | High | HIGH | detect | Tier 4 | ✅ PASS |
| CS-04 | AML Structuring | TM | Medium | CRITICAL | detect | Tier 3 | ✅ PASS |
| CS-05 | Chinese Wall Breach | CS | High | CRITICAL | detect | Tier 4 | ✅ PASS |
| CS-06 | Wash Trading | TM | High | HIGH | detect | Tier 2 | ✅ PASS |
| CS-07 | Regulatory Change | RU | Medium | MEDIUM | detect | Tier 2 | ✅ PASS |
| CS-08 | Misleading Marketing | CS | Low-Med | CRITICAL | detect | Tier 4 | ✅ PASS |
| CS-09 | Sanctions Violation | TM+RU | High | CRITICAL | detect | Tier 3 | ✅ PASS |
| CS-10 | Front-Running | TM | Medium | CRITICAL | detect | Tier 3 | ✅ PASS |
| CS-11 | Data Privacy | CS+RU | Medium | HIGH | detect | Tier 2 | ✅ PASS |
| CS-12 | Concentration Risk | TM | Low | MEDIUM | detect | Tier 2 | ✅ PASS |
| CS-13 | Off-Channel Comms | CS | Medium | HIGH | detect | Tier 2 | ✅ PASS |
| CS-14 | Late Trading | TM | Medium | CRITICAL | detect | Tier 3 | ✅ PASS |
| CS-15 | Best Execution | TM | Medium | HIGH | detect | Tier 2 | ✅ PASS |
| CS-16 | Research Independence | CS+TM | High | CRITICAL | detect | Tier 4 | ✅ PASS |
| CS-17 | Elder Exploitation | TM+CS | High | CRITICAL | detect | Tier 3 | ✅ PASS |
| CS-18 | FALSE POSITIVE | TM | Medium | NO ALERT | no_detect | None | ✅ PASS |
| CS-19 | Multi-Jurisdiction | RU | High | HIGH | detect | Tier 2 | ✅ PASS |
| CS-20 | Coordinated AML | ALL | Very High | CRITICAL | detect | Tier 4 | ✅ PASS |

## Summary Statistics

- **Total Scenarios:** 20
- **Detection Consensus:** 19/20 (95%) — CS-18 correctly suppressed
- **Escalation Rate:** 19/20 (95%)
- **CS-18 (False Positive):** ✅ Correctly suppressed (no detection, no escalation)
- **CS-20 (Coordinated):** ✅ All 4 agents coordinated
- **Correct Escalation Tier:** 19/20 (95%) — all escalations land on the documented tier

## Notes

- CS-09 (Sanctions): TM-001 flags the wire transfer to the SDN-listed beneficiary (HIGH, 0.70) and RU-001 confirms via the SDN list update (CRITICAL, 0.85) → consensus DETECT, escalated to Tier 3 (Manager) with SAR filing authority.
- CS-12 (Concentration): TM-001 detects the sector limit breach (MEDIUM, 0.72); single-agent detection reaches consensus DETECT and escalates to Tier 2 (Senior Analyst), consistent with the other single-agent MEDIUM scenarios (e.g., CS-07).
- All CRITICAL severity scenarios correctly escalate to Tier 3 or Tier 4
- All HIGH severity scenarios correctly escalate to Tier 2 or higher