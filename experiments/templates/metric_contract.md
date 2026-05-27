# Metric Contract

Status: incomplete

## Primary Objective

- Metric:
- Direction: maximize
- Business/scientific goal:
- Minimum practical delta:

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

