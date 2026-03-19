---
name: experiment-report
description: Generate a structured, stakeholder-ready experiment report from A/B test results. Supports technical and executive audiences.
---

Generate a complete experiment report. Use context from the conversation (prior analysis, experiment design) or gather the needed information from `$ARGUMENTS` and follow-up questions.

## Required Information

Collect before generating:
- Experiment name and description
- Hypothesis
- Primary and secondary metrics with results
- Guardrail metrics status
- Sample sizes, duration, and allocation
- Statistical method and results (p-value, CI, effect size)
- Segment breakdowns (if available)

Ask the user for their **target audience**:
- **Technical** (default): Full statistical detail, code references, methodology discussion
- **Executive**: Simplified, focused on business impact and recommendation

## Report Structure

Generate a Markdown report with these sections:

### Executive Summary
2-3 sentences: what was tested, what happened, what the recommendation is. This should be understandable by anyone without reading further.

### Background and Hypothesis
- What problem or opportunity motivated the experiment
- The specific hypothesis being tested
- Link to the original experiment design doc if available

### Methodology
- Randomization unit and target population
- Traffic allocation and experiment duration
- Sample sizes per variant
- Statistical test(s) used and significance threshold
- Any pre-registered analysis plan

### Results

**Primary Metric:**
- Control vs. Treatment values
- Absolute and relative difference
- 95% confidence interval
- P-value and significance determination
- Effect size

**Secondary Metrics:**
Present in a table:
| Metric | Control | Treatment | Diff (%) | 95% CI | p-value | Significant? |
|--------|---------|-----------|----------|--------|---------|-------------|

**Guardrail Metrics:**
| Metric | Control | Treatment | Status |
|--------|---------|-----------|--------|
For each guardrail, mark PASS (no degradation) or FAIL (significant degradation detected).

### Segment Analysis
If segment data is available, break down the primary metric by key dimensions:
- Platform (web, iOS, Android)
- Geography
- New vs. returning users
- Other relevant segments

Flag any segments where results diverge significantly from the overall result.

### Discussion
- Statistical significance vs. practical significance
- Potential confounds or limitations
- Novelty effect considerations
- What the results do NOT tell us
- Open questions for follow-up

### Recommendation
One of:
- **Ship**: Results are positive and significant. State expected impact at full rollout.
- **Iterate**: Results are mixed or inconclusive. State what to change and test next.
- **Kill**: Results are negative or guardrails were violated. State the evidence.

Provide clear reasoning linking the data to the recommendation.

### Appendix
- Raw data tables
- Analysis code or link to notebook
- SRM check results
- Power analysis details

## Guidelines

- For **executive** audience: collapse Methodology and Appendix into brief notes; lead with business impact numbers; avoid jargon; use a "what this means" callout after any statistical result.
- For **technical** audience: include full statistical detail; reference specific tests and assumptions; include reproducible code.
- Use clear, direct language throughout. Avoid hedging unless uncertainty is genuinely warranted.
