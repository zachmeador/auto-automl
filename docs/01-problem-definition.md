# Problem definition

## Goal

Write a testable prediction contract before inspecting model results. The contract defines what is predicted, when it is predicted, how errors are valued, and which constraints the final model must satisfy.

## Required decisions

### Prediction contract

- **Unit:** The entity represented by one prediction, such as a customer, transaction, device-hour, or patient visit.
- **Population:** Which units are eligible. State inclusion and exclusion rules.
- **Observation time:** The latest instant from which input data may be used.
- **Target:** The outcome, its exact derivation, label window, units, and valid values.
- **Horizon:** How far after observation time the outcome is predicted.
- **Task:** Classification, regression, ranking, forecasting, survival analysis, or another explicit formulation.
- **Output:** Class, score, probability, numeric estimate, interval, or ranked list.

Example: “For each completed account signup, estimate within one second the probability of cancellation during the next 30 days, using only information available when signup completes.”

### Success criteria

Choose one primary model-selection metric. Connect it to the actual cost of false positives, false negatives, overprediction, or underprediction. Define:

- the metric and its direction;
- the evaluation population;
- any averaging or weighting;
- an acceptance threshold;
- a simple baseline and, when available, the current process;
- secondary metrics that expose important tradeoffs.

For classification, decide whether evaluation concerns ranking, fixed-threshold decisions, or probability quality. For regression, state whether large errors deserve disproportionate weight and whether target scale makes relative errors meaningful. If a decision threshold will be tuned, specify the cost or capacity rule used to tune it.

### Constraints and risks

Record hard limits separately from preferences:

- training time and compute budget;
- prediction latency, throughput, memory, and artifact size;
- explainability or monotonicity requirements;
- privacy, licensing, retention, and access restrictions;
- subgroup performance or fairness requirements;
- human-review and override requirements;
- retraining cadence and expected data drift;
- consequences of delayed, missing, or incorrect predictions.

List intended users, permitted uses, prohibited uses, and material failure modes. The [NIST AI Risk Management Framework](https://airc.nist.gov/airmf-resources/airmf/) provides a common vocabulary for validity, reliability, safety, privacy, fairness, transparency, and security.

## Procedure

1. Write the contract using domain language.
2. Trace target creation and feature availability on a timeline.
3. Confirm that labels exist soon enough and in sufficient quantity for evaluation.
4. Define the baseline, metrics, constraints, and decision rule.
5. Review leakage paths, invalid uses, and harms with domain owners.
6. Freeze a versioned specification. Later changes must be recorded as new experiment assumptions.

## Deliverables

- Versioned prediction contract.
- Target derivation and feature-availability cutoff.
- Metric definitions, baseline, and acceptance thresholds.
- Resource and operational constraints.
- Intended-use statement and risk register.

## Exit criteria

The stage is complete when an independent reader can determine which rows receive predictions, which information is legal at prediction time, how the target is computed, how success is scored, and why the model would or would not be acceptable.
