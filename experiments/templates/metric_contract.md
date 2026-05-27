# Metric Contract

Status: incomplete

Project ID:
Project root: `projects/<project_id>/`

## Primary Objective

- Metric:
- Direction: maximize
- Business/scientific goal:
- Minimum practical delta:

## Project Goal

Default goal: produce the best leakage-clean validation candidate under the declared metric and budget, without accessing the sealed final holdout.

Override goal:

## Stop Policy

Stop the project loop when any of these conditions is true:

- Max run budget reached: 10 runs by default if not overridden
- Time/cost budget reached: unset by default
- No admitted run improves by the minimum practical delta for this many consecutive iterations: 3 admitted iterations by default
- User-requested target metric reached: unset by default
- Leakage or metric blockers prevent further valid progress: always active
- Human requests final holdout release gate: always active

Do not claim the project is complete after a single experiment unless one stop condition is satisfied.

When this contract leaves a defaultable field blank, use these defaults:

- max run budget: 10
- no-improvement patience: 3 admitted iterations
- time/cost budget: no limit unless specified
- target metric: no target unless specified
- minimum practical delta: must be task-specific; if absent, mark the metric contract incomplete and block model search

## Tie-Breakers

- Secondary metric 1:
- Secondary metric 2:
- Runtime:
- Memory:
- Inference latency:

## Baseline

- Baseline run ID:
- Baseline metric value:
- Baseline artifact:

## Statistical Evidence

- Required folds:
- Required repeated seeds:
- Confidence interval requirement:
- Close-call rule:

## Constraints

- Calibration:
- Class-specific recall/precision:
- Fairness:
- Cost-sensitive errors:
- Interpretability:

## Admission Rule

A run is leaderboard-admissible only when:

- leakage verdict is `PASS`
- metric review verdict is `PASS`
- primary metric improves over baseline by at least the minimum practical delta, unless this is the first baseline
- all hard constraints are satisfied
