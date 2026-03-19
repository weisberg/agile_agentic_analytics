# Behavioral Pattern Analysis Methodology

Markov chain path analysis and content affinity scoring for web behavioral
data.

## Markov Chain Path Analysis

### Overview

Navigation path analysis models user sessions as sequences of page visits and
estimates transition probabilities between pages. This skill uses second-order
(bigram) Markov chains, where the probability of visiting the next page
depends on the current page AND the previous page, providing more accurate
path modeling than first-order chains.

### State Representation

Each state in the Markov chain is a tuple of the two most recently visited
pages:

```
State = (page_{t-1}, page_{t})
Transition: P(page_{t+1} | page_{t-1}, page_{t})
```

Special states:
- `(START, START)` — session entry before any page is visited.
- `(page_{t-1}, CONVERT)` — absorbing state for sessions that convert.
- `(page_{t-1}, EXIT)` — absorbing state for sessions that end without
  conversion.

### Transition Matrix Construction

1. Parse each session into an ordered sequence of page paths.
2. Prepend `START` and append `CONVERT` or `EXIT` based on session outcome.
3. For each consecutive triplet `(p_{i-1}, p_i, p_{i+1})`, increment the count
   for transition `(p_{i-1}, p_i) -> p_{i+1}`.
4. Normalize each row to produce transition probabilities.

### Conversion Path Identification

To find the highest-probability paths to conversion:

1. Enumerate paths from `(START, START)` to any `(*, CONVERT)` state using
   beam search (beam width = 50).
2. Path probability = product of all transition probabilities along the path.
3. Rank paths by probability and report the top K (default K = 10).

### Removal Effect (Channel Attribution)

The removal effect measures each page's contribution to conversion:

1. For each page P, set all transition probabilities out of states containing
   P to redirect to `EXIT`.
2. Recompute the overall conversion probability from `(START, START)`.
3. Removal effect of P = (baseline conversion probability - modified
   conversion probability) / baseline conversion probability.

Pages with higher removal effects are more critical to the conversion path.

### Dead-End Detection

A page is classified as a dead end if:

- It has an exit rate above the 90th percentile across all pages, AND
- It is NOT a natural terminal page (e.g., confirmation, thank-you).

### Loop Detection

An unexpected loop exists when:

- The transition `(A, B) -> A` has probability > 0.1 (users bounce between
  A and B).
- Sessions containing the loop have conversion rates significantly below the
  site average (z-test, p < 0.05).

## Content Affinity Scoring

### Definition

Content affinity measures the correlation between visiting a content category
and subsequent conversion. It answers: "Which types of content are associated
with higher conversion rates?"

### Calculation

For each content category C:

```
affinity_score(C) = P(convert | visited C) / P(convert)
```

Where:
- `P(convert | visited C)` = conversions among sessions that included at
  least one page in category C / total sessions that visited category C.
- `P(convert)` = overall site conversion rate.

An affinity score > 1.0 indicates the category is positively associated with
conversion; < 1.0 indicates negative association.

### Statistical Significance

Test each affinity score with a chi-squared test of independence:

| | Converted | Did Not Convert |
|---|---|---|
| Visited C | a | b |
| Did Not Visit C | c | d |

Apply Benjamini-Hochberg correction for multiple comparisons across all
content categories. Only report affinity scores where the adjusted p-value
< 0.05.

### Confidence Interval

Compute the 95% confidence interval for the affinity score using the log
method:

```
log(affinity) +/- 1.96 * sqrt(1/a - 1/(a+b) + 1/c - 1/(c+d))
```

### Content Category Assignment

Pages are assigned to content categories using one of:

1. **GA4 content groups** — if configured in the GA4 property.
2. **URL pattern matching** — regex rules mapping URL path patterns to
   categories (e.g., `/blog/*` -> "Blog", `/products/*` -> "Product").
3. **Manual mapping** — a CSV lookup table of page path to category.

The mapping method should be specified in the extraction configuration.

## Exit Rate Analysis (Conversion-Weighted)

### Weighted Exit Rate

Standard exit rate treats all exits equally. Conversion-weighted exit rate
assigns higher importance to exits that occur closer to the conversion step
in the dominant navigation path.

```
weighted_exit_rate(P) = exit_rate(P) * proximity_weight(P)
```

Where `proximity_weight(P)` is inversely proportional to the average number
of steps between page P and conversion in the Markov chain:

```
proximity_weight(P) = 1 / (1 + avg_steps_to_conversion(P))
```

Pages with high weighted exit rates are high-priority optimization targets
because users are abandoning close to conversion.

## Implementation Notes

- Second-order Markov chains can produce large state spaces. For sites with
  >1000 unique pages, aggregate low-traffic pages into an "Other" category
  (pages below the 5th percentile of pageviews).
- Transition matrices should be stored as sparse matrices (scipy.sparse) for
  memory efficiency.
- Path enumeration uses beam search rather than exhaustive enumeration to keep
  computation tractable.
- All scoring outputs include sample sizes so downstream consumers can assess
  reliability.
