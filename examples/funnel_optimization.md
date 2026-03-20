# Worked Example: Funnel Analysis + Conversion Optimization

End-to-end walkthrough from raw web events to CRO hypotheses with revenue
impact estimates. Uses the synthetic `events.csv` (10,000 rows, 2,000 users,
90 days of behavioral data).

## Overview

| Step | What Happens | Output |
|------|-------------|--------|
| 1 | Load events and build the funnel | Step-by-step conversion rates |
| 2 | Identify bottlenecks | Ranked drop-off points |
| 3 | Estimate revenue impact | Dollar value per 1pp improvement at each step |
| 4 | Generate CRO hypotheses | Prioritized test ideas |

## Setup

```bash
python examples/generate_sample_data.py
mkdir -p workspace/raw
cp examples/data/events.csv workspace/raw/
```

---

## Step 1: Build the Funnel

```
/marketing-analytics:funnel-analysis events.csv
```

The skill will:

1. **Load and validate** `workspace/raw/events.csv`, confirming `user_id`,
   `event_name`, and `timestamp` columns.
2. **Detect the funnel sequence** from event frequency patterns:
   `page_view` -> `add_to_cart` -> `begin_checkout` -> `purchase`.
3. **Compute per-step conversion rates** using unique users per step.

### Expected Funnel Output

```
Step              | Users  | Step CVR | Cumulative CVR | Drop-off
------------------+--------+----------+----------------+---------
page_view         |  2,000 |     --   |        100.0%  |     --
add_to_cart       |  ~600  |   30.0%  |         30.0%  |  70.0%
begin_checkout    |  ~300  |   50.0%  |         15.0%  |  50.0%
purchase          |  ~180  |   60.0%  |          9.0%  |  40.0%
```

The synthetic data was designed with these approximate conversion rates:
- 30% of page viewers add to cart
- 50% of add-to-cart users begin checkout
- 60% of checkout starters complete purchase
- Overall: ~9% page-view-to-purchase conversion

---

## Step 2: Identify Bottlenecks

The skill ranks funnel steps by **absolute user drop-off** (not just
percentage):

```
Bottleneck Ranking (by users lost):

1. page_view -> add_to_cart:    ~1,400 users lost (70% drop-off)
2. add_to_cart -> begin_checkout: ~300 users lost (50% drop-off)
3. begin_checkout -> purchase:    ~120 users lost (40% drop-off)
```

**Key insight**: The page_view-to-add_to_cart step loses the most users in
absolute terms, but this is typical for top-of-funnel. The
add_to_cart-to-begin_checkout step (50% drop-off) is often the most
*improvable* because users have already shown purchase intent.

The skill also checks for:

- **Time-between-steps** anomalies -- long delays suggest friction.
- **Page-level patterns** -- which product pages have higher/lower
  add-to-cart rates.
- **Device or segment splits** (if the data includes those dimensions).

---

## Step 3: Estimate Revenue Impact

The skill computes the dollar value of improving each conversion step by
1 percentage point. This requires either:

- An average order value (AOV) parameter, or
- Linking to `transactions.csv` for observed AOV.

Assuming AOV of $75 (typical for the sample transaction data):

```
Revenue Impact per 1pp Improvement:

Step                        | +1pp Users | Added Revenue/Month
----------------------------+------------+--------------------
page_view -> add_to_cart    |    +20     | +$1,500
add_to_cart -> begin_checkout|   +6      | +$450
begin_checkout -> purchase  |    +3      | +$225
```

**Interpretation**: A 1 percentage point lift at the top of the funnel has
the largest absolute impact because it operates on the largest user base.
However, lower-funnel improvements often have higher confidence of
achievability since the audience is more qualified.

---

## Step 4: Generate CRO Hypotheses

Based on the bottleneck analysis, the skill generates prioritized test ideas:

### High Priority: Add-to-Cart Rate (30% baseline)

| Hypothesis | Expected Lift | Effort |
|-----------|--------------|--------|
| Add social proof (review count) on product pages | +2-4pp | Low |
| Implement sticky add-to-cart button on mobile | +1-3pp | Medium |
| Show estimated delivery date above the fold | +1-2pp | Low |

### Medium Priority: Cart-to-Checkout Rate (50% baseline)

| Hypothesis | Expected Lift | Effort |
|-----------|--------------|--------|
| Add progress indicator to checkout flow | +2-5pp | Low |
| Implement guest checkout option | +3-8pp | Medium |
| Show cart total with shipping estimate earlier | +1-3pp | Low |

### Lower Priority: Checkout Completion (60% baseline)

| Hypothesis | Expected Lift | Effort |
|-----------|--------------|--------|
| Add trust badges near payment form | +1-3pp | Low |
| Offer alternative payment methods | +2-5pp | High |
| Reduce form fields (auto-detect city from zip) | +1-2pp | Medium |

---

## Combining with Other Skills

### Segment-Level Funnels

Run segmentation first, then funnel analysis with segments:

```
/marketing-analytics:audience-segmentation transactions.csv
/marketing-analytics:funnel-analysis events.csv --by-segment
```

This reveals whether certain customer segments have dramatically different
conversion patterns. For instance, returning Champions might convert at 18%
while new visitors convert at 4% -- implying different optimization
strategies for each group.

### Feed Hypotheses into Experimentation

Take the top CRO hypothesis and design an A/B test:

```
/marketing-analytics:experimentation --hypothesis "Adding social proof increases add-to-cart rate by 3pp" --baseline-cvr 0.30 --mde 0.03
```

The experimentation skill will calculate the required sample size, expected
test duration, and recommend a testing methodology (frequentist or
sequential).

---

## Key Takeaways

1. **Absolute drop-off matters more than percentage** for prioritization.
   A 70% drop at the top of funnel loses more revenue than a 40% drop at
   the bottom.
2. **Revenue impact estimation** turns abstract conversion rates into
   dollar values that stakeholders can act on.
3. **CRO hypotheses should be testable** -- each one maps naturally to an
   A/B test that the experimentation skill can design and analyze.
4. **Segment-level funnels** often reveal that a single aggregate
   bottleneck masks very different behaviors across customer types.
