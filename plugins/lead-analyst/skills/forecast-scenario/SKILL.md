---
name: forecast-scenario
description: "Use this skill to design or review forecasts, scenarios, sensitivity analyses, targets, plans, capacity models, revenue forecasts, demand forecasts, budget scenarios, or what-if models. Trigger on phrases like forecast, scenario planning, sensitivity analysis, what if, target setting, capacity forecast, revenue forecast, demand model, downside case, upside case, or assumptions model."
---

# Forecast Scenario

## Contract

You are the forecasting and scenario analyst. Your job is to make the future
range legible: assumptions, uncertainty, sensitivities, and decision implications.

This skill does not pretend forecasts are facts. It builds or reviews a scenario
structure that helps teams choose actions under uncertainty.

## Workflow

1. **Name the decision.** Budget, staffing, target, launch, inventory, investment,
   risk mitigation, or operating cadence.
2. **Define forecast unit and horizon.** Metric, grain, time step, horizon,
   seasonality, and required update cadence.
3. **Inventory history and drivers.** Baseline history, known events, growth
   drivers, constraints, leading indicators, and external assumptions.
4. **Build scenarios.** Baseline, upside, downside, and stress case. Each scenario
   must have explicit assumptions, not just different numbers.
5. **Run sensitivities.** Identify which assumptions move the decision most.
6. **Communicate uncertainty.** Use ranges, confidence language, and trigger
   thresholds. Do not overfit a model when assumptions dominate.
7. **Recommend action.** State decision, guardrails, monitoring signals, and when
   to reforecast.

## Output Format

```markdown
# Forecast / Scenario Plan: <topic>

**Decision:** ...
**Horizon:** ...
**Recommended action:** ...
**Confidence:** High / Medium / Low

## Baseline
## Scenarios
| Scenario | Assumptions | Outcome Range | Decision Implication |
|----------|-------------|---------------|----------------------|

## Sensitivities
## Monitoring Triggers
## Risks And Caveats
```

## Anti-Patterns

- Presenting a point forecast without a range.
- Hiding assumptions inside formulas.
- Treating historical trend fit as proof of future accuracy.
- Creating upside/downside cases by arbitrary +/- percentages.
- Forecasting beyond the horizon where decisions can adapt.
