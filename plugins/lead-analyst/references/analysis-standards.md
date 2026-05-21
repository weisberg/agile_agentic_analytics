# Lead Analyst Analysis Standards

Use these standards across lead-analyst skills and agents.

## The Analytical Spine

1. **Decision.** What decision, recommendation, or next action should this analysis inform?
2. **Metric.** What is the exact numerator, denominator, grain, time window, and ownership of each metric?
3. **Population.** Who or what is included, excluded, and newly missing because of filters or joins?
4. **Evidence.** What data, documents, notes, dashboards, or prior analyses support the answer?
5. **Quality.** Is the evidence fresh, complete, deduplicated, comparable, and measured consistently?
6. **Interpretation.** Which claims are descriptive, correlational, experimental, causal, or judgment calls?
7. **Decision.** What should the team do, how confident are we, and what would change the recommendation?

## Evidence Ladder

| Level | Evidence Type | How To Use It |
|-------|---------------|---------------|
| L1 | Anecdote, stakeholder memory, single quote | Useful for hypotheses, not for sizing or decisions alone. |
| L2 | Dashboard or report without raw query/provenance | Treat as directional until definitions and filters are verified. |
| L3 | Reproducible query, notebook, or source extract | Good for descriptive decisions if quality checks pass. |
| L4 | Controlled experiment, holdout, or strong quasi-experiment | Best for causal claims when design and instrumentation hold up. |
| L5 | Repeated evidence across methods and time | Strongest basis for durable operating decisions. |

## Default Quality Checks

- Freshness and coverage by time period.
- Duplicates at the analysis grain.
- Missingness by key segment and time.
- Join loss and unmatched IDs.
- Metric definition drift across source systems.
- Outliers, censoring, and unit/currency mismatches.
- Selection bias from filters, eligibility, survivorship, or channel exposure.

## Communication Standard

Lead with the answer. Then show the evidence, caveats, and next action. A useful
brief makes a decision easier without hiding uncertainty.
