---
name: feature-engineer
description: Propose and implement fold-safe feature engineering changes inside an AutoML worker iteration.
---

# Feature Engineering Skill

Use this skill when the selected experiment changes features, transforms, encodings, imputations, or feature selection.

A feature-engineering experiment may include a bounded inner search over a declared feature family, such as comparing a small set of encodings, binning strategies, lag windows, or feature-selection thresholds. The search must be declared before execution, fold-safe, and fully recorded.

## Hard Rules

- Fit all learned transformations on training folds only.
- Put transformations inside a pipeline, fold loop, or equivalent split-aware structure.
- Never compute target encodings, aggregations, scalers, imputers, PCA, feature selection, oversampling, or text/vector features on all data before splitting.
- For time-series features, use only information available at prediction time.
- For grouped data, do not aggregate across validation/test groups in ways unavailable at training time.
- Define feature-search spaces before execution when comparing multiple feature variants.
- Record every feature variant that can influence future choices.

## Procedure

1. Read dataset, split, and metric contracts.
2. Pick one feature hypothesis.
3. If comparing variants, define the bounded feature-search space and selection rule before running it.
4. Write the hypothesis and leakage risks into the run plan.
5. Implement the feature change in the smallest reasonable surface area.
6. Add or run checks that prove the transform is fit only on allowed training data.
7. Record feature names, source columns, variants tried, and whether each feature is learned, deterministic, target-aware, temporal, or grouped.

## Preferred Feature Categories

Start with interpretable, bounded changes:

- missingness indicators
- numeric transforms with fixed formulas
- categorical encodings inside folds
- interaction terms suggested by domain semantics
- monotonic binning or clipping based on training quantiles
- time-lag and rolling-window features with explicit horizon checks

## Avoid Unless Explicitly Justified

- features derived from validation/test distribution statistics
- target encoding outside nested CV
- high-cardinality memorization features
- post-outcome status columns
- global aggregates over all rows
- any feature that improves validation sharply without a plausible deployment-time explanation

## Output

Update the run artifacts with:

- feature hypothesis
- implementation summary
- feature list
- leakage risks and mitigations
- validation metrics
- reproducibility notes
