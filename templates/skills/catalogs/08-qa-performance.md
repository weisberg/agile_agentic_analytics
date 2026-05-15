# QA and Performance Components

Route inference, browser QA fix loops, test bootstrap, health scoring, performance budgets, and canary monitoring.

Components: 67-72.

Source: distilled from the gstack `SKILL.md` corpus. Each component includes a context paragraph, reusable description, and compact sample.

## **67. QA Route Inference Component**

**Reusable purpose:** Map code changes to the browser routes most likely affected.

**Context:** Use this for diff-aware QA when the user did not provide exact routes to test. It maps changed files to likely pages and flows, records confidence, and falls back to homepage/navigation exploration so browser testing is guided by the actual code touched.

**Reusable flow:**

```text
1. Read git diff.
2. Identify changed frontend files, route files, controllers, pages, and components.
3. Infer affected URLs.
4. If uncertain, test homepage plus top navigation and changed-feature entry points.
5. Record inference confidence in the QA report.
```

**Use this for:** Diff-aware web QA, PR smoke testing, release checks.

**Sample:**

```text
Changed files:
- app/controllers/admin/imports_controller.rb
- app/views/admin/imports/show.html.erb
- app/javascript/components/ImportFailureTable.tsx

Inferred routes:
- /admin/imports
- /admin/imports/:id

Confidence: high, route and view files match directly.
```

------

## **68. Browser QA Fix Loop Component**

**Reusable purpose:** Test as a user, fix verified defects, and re-test before claiming success.

**Context:** Use this when a QA skill is allowed to fix bugs, not just report them. It ties together reproduction, source-cause identification, one atomic fix, regression coverage, targeted tests, and browser re-verification so the final claim is grounded in user-visible behavior.

**Reusable loop:**

```text
1. Establish baseline screenshot and console/network state.
2. Exercise primary user flow.
3. Reproduce defect.
4. Identify source cause.
5. Apply one atomic fix.
6. Add or update regression test if behavior changed.
7. Re-run targeted tests.
8. Re-open browser and verify user-visible fix.
9. Commit only if the skill owns commits and verification passed.
```

**Use this for:** QA, design review fix mode, release hardening.

**Sample:**

```text
QA loop:
1. Reproduce: mobile import table overflows viewport.
2. Root cause: fixed 960px min-width on table wrapper.
3. Fix: add responsive horizontal scroll and sticky first column.
4. Test: add mobile viewport browser test.
5. Verify: screenshot at 390px shows no page overflow.
6. Commit: "Fix mobile import failure table overflow".
```

------

## **69. Test Bootstrap Component**

**Reusable purpose:** Add the first useful test infrastructure when a project has none.

**Context:** Use this when a project lacks the test infrastructure needed to verify the current change. It lets the skill add the smallest appropriate test framework and one real useful test, avoiding both no coverage and overbuilt testing scaffolds.

**Reusable rules:**

```text
- Detect existing framework before adding one.
- Prefer the project's ecosystem-standard test tool.
- Add one real regression or smoke test, not just config.
- Keep bootstrap minimal.
- Run the new test and document the command.
```

**Use this for:** QA, ship, new repo quality gates.

**Sample:**

```text
No browser tests detected.

Bootstrap:
- Use Playwright because package.json already includes Vite and npm scripts.
- Add one smoke test for /admin/imports/:id.
- Add npm script `test:e2e`.
- Run `npm run test:e2e`.
- Document command in the QA report.
```

------

## **70. Weighted Health Score Component**

**Reusable purpose:** Convert multiple quality checks into one explainable health score.

**Context:** Use this for health dashboards or QA reports that need to summarize several quality signals in one digestible score. It works best when categories may differ by project, because weights can be redistributed and missing tools can be separated from actual failures.

**Reusable categories:**

```text
typecheck
lint
tests
coverage
dead_code
security
performance
docs
browser_health
```

**Rules:**

```text
- Redistribute weights when a category is not applicable.
- Separate missing-tool warnings from actual failures.
- Persist trend history.
- Show top three highest-leverage improvements.
```

**Patterns copied from:** `health`, `qa`, `benchmark`, `cso`.

**Sample:**

```yaml
health_score:
  total: 86
  categories:
    typecheck: {weight: 20, score: 100}
    lint: {weight: 15, score: 90}
    tests: {weight: 30, score: 80}
    security: {weight: 15, score: 85}
    browser_health: {weight: 20, score: 75}
  top_improvements:
    - Add mobile regression test.
    - Fix one lint warning in import table.
```

------

## **71. Performance Budget Component**

**Reusable purpose:** Detect web performance regressions with baseline comparison.

**Context:** Use this for performance-sensitive routes, dashboards, landing pages, and release checks where regressions can be measured. It defines budgets for requests, bytes, timing, and resources so the skill can compare current behavior against an explicit threshold or historical baseline.

**Reusable metrics:**

```text
- page load timings
- request count
- total transferred bytes
- JS bytes
- CSS bytes
- slowest resources
- console errors
- key user timing marks
```

**Reusable threshold posture:**

```text
regression:
  material slowdown or budget breach
warning:
  noticeable but not release-blocking drift
ok:
  within threshold
```

**Use this for:** Benchmarking, PR checks, canary monitoring, release gates.

**Sample:**

```yaml
performance_budget:
  route: /admin/imports/123
  max_requests: 35
  max_js_kb: 250
  max_lcp_ms: 2500
  current:
    requests: 28
    js_kb: 214
    lcp_ms: 1720
  verdict: ok
```

------

## **72. Canary Monitor Component**

**Reusable purpose:** Watch production or staging after deploy against a known-good baseline.

**Context:** Use this after deploying or during production rollout when the risk is not known until real pages are monitored. It watches baseline-relative changes across screenshots, console, network, and timings, and avoids false alarms by requiring consecutive failures before escalating.

**Reusable flow:**

```text
1. Capture baseline screenshot, console, network, and timing.
2. Poll target pages during deploy window.
3. Require consecutive failures before alerting.
4. Classify visual, network, console, and performance changes.
5. Offer investigate, continue, rollback, or dismiss.
6. Write canary report with timeline and verdict.
```

**Use this for:** Deployments, migrations, DNS/CDN changes, visual-risk releases.

**Sample:**

```text
Canary watch:
- Baseline: /admin/imports and /admin/imports/123 before deploy.
- Poll interval: 60 seconds.
- Failure threshold: 2 consecutive failures.
- Watch: screenshot diff, console errors, 5xx responses, LCP regression.
- On alert: offer investigate, rollback, continue, or dismiss.
```
