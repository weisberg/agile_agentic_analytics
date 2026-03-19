---
name: review-experiment
description: Review experiment implementation code for common A/B testing pitfalls — assignment bugs, logging gaps, bucketing leaks, and feature flag issues.
---

Review experiment implementation code for A/B testing correctness. Accept a file path, code block, or directory from `$ARGUMENTS` or the conversation context.

Read the relevant code, then systematically check for issues in each category below. Reference specific lines in your findings.

## Review Categories

### 1. Assignment Correctness
- Is the randomization deterministic and consistent? (Same user always gets same variant)
- Is a proper hash function used? (MD5/SHA on user ID + experiment salt, not `Math.random()`)
- Is the randomization unit correct? (User-level for most experiments, not request/session-level)
- Is the experiment salt unique? (Prevents correlation between experiments)
- Is the traffic allocation implemented correctly? (Hash modulo or range check)

### 2. Bucketing Stability
- Can a user switch variants mid-experiment?
  - Cookie deletion or expiration
  - Logged-in vs. logged-out state
  - App updates changing assignment logic
  - Server-side vs. client-side assignment inconsistency
- Is the assignment cached appropriately for the session/request lifecycle?

### 3. Exposure Logging
- Is the exposure event logged at the **point of divergence** — the exact moment the user's experience differs?
- Is exposure logged BEFORE the feature is shown (not after interaction)?
- Is exposure logged for BOTH control and treatment?
- Are there code paths where a user is assigned but never exposed (intent-to-treat issues)?
- Is the exposure event deduplicated appropriately?

### 4. Metric Instrumentation
- Are conversion events correctly attributed to the variant the user was assigned to?
- Is there risk of double-counting conversions?
- Are timestamps consistent between exposure and conversion events?
- For server-side metrics: is the variant correctly propagated through the request context?

### 5. Feature Flag Hygiene
- Is the feature flag checked consistently across ALL code paths?
- Are default/fallback values correct? (What happens if the experiment service is down?)
- Are there race conditions between flag evaluation and rendering?
- Is the flag evaluated once and reused, or re-evaluated multiple times with potential inconsistency?

### 6. Performance
- Does the experiment add latency to the critical path?
- Is the feature flag evaluation on the hot path? Could it be cached?
- Are experiment assignments batched or fetched one-at-a-time?
- Does the treatment variant load additional resources (JS, images) that could affect performance metrics?

### 7. Cleanup and Interactions
- Is there dead code from previous experiments that should be removed?
- Are multiple experiments nesting or interacting unintentionally?
- Is the experiment properly scoped to avoid affecting unrelated features?
- Is there a clear plan for cleanup after the experiment concludes?

## Output Format

Structure your review as:

**Summary:** One paragraph overall assessment.

**Findings:**

For each issue found:

> **[SEVERITY] Title**
> File: `path/to/file.py:42`
>
> Description of the issue and why it matters.
>
> **Fix:**
> ```
> suggested code change
> ```

Severity levels:
- **CRITICAL**: Will produce invalid experiment results. Must fix before launch.
- **WARNING**: Risk of data quality issues. Should investigate.
- **INFO**: Best practice suggestion. Nice to fix but not blocking.

**Verdict:** Overall assessment — safe to launch, needs fixes, or needs redesign.

## Guidelines

- Focus on issues specific to experimentation. Don't review general code quality unless it directly impacts experiment correctness.
- If you can't find the experiment assignment logic, flag that as a critical issue.
- If the code uses an experimentation framework/SDK, check that it's being used correctly per its conventions.
- When in doubt, flag it. Better to over-report than miss a bucketing bug.
