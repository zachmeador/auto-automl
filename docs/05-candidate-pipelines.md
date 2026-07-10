# Candidate pipelines

## Goal

Define the complete set of valid preprocessing, estimator, and hyperparameter combinations that search may evaluate. The candidate registry is an executable experiment specification, not a list of model names.

## Start with baselines

Include at least one trivial baseline using the same folds and metric as trained models:

- majority class, stratified random class, or prior probability for classification;
- mean, median, or seasonal-naive prediction for regression or forecasting;
- current production rule or incumbent model when available.

A candidate must beat the relevant baseline by the declared acceptance margin, not merely produce a valid score.

## Select model families

Choose families that cover useful inductive biases without adding redundant options. Check each family against:

- task and output type;
- row and feature counts;
- dense or sparse inputs;
- nonlinearities and interactions;
- native categorical or missing-value support;
- class weighting or sample weighting;
- probability, interval, or ranking support;
- training and prediction cost;
- artifact size and runtime dependencies;
- explanation, monotonicity, or audit requirements.

A typical tabular search might include a regularized linear model as a stable reference, a tree ensemble for nonlinear interactions, and a boosting model for stronger structured-data performance. More families are not automatically better; every added degree of freedom increases compute and selection risk.

## Define complete pipelines

For each model family, specify:

1. compatible feature subsets and semantic types;
2. required imputation, encoding, scaling, or feature extraction;
3. optional transformations that search may enable;
4. estimator construction and prediction interface;
5. post-processing such as calibration or decision thresholding;
6. resource controls, seeds, and thread limits.

Do not force all estimators through identical preprocessing. Scaling may be essential for one family and unnecessary for another; dense one-hot features may be acceptable for a linear model but prohibitive elsewhere.

## Define search spaces

Each tunable parameter needs a type, bounds, sampling distribution, and condition.

- Sample scale parameters such as regularization or learning rate on a log scale.
- Bound capacity parameters using dataset size and resource limits.
- Express conditional choices: a parameter exists only when its parent option is active.
- Reject invalid combinations before fitting.
- Keep fixed values visible in the recorded configuration.
- Avoid tuning parameters that cannot materially affect the declared objective.

Search spaces should be broad enough to reveal underfitting and overfitting, but finite and defensible. Record the rationale for important bounds.

## Preflight validation

Before full search, run each family on one small training/validation slice and verify:

- construction, fit, and prediction complete;
- output shape and type match the scorer;
- class labels and probabilities have stable ordering;
- sample weights and groups are routed correctly when required;
- preprocessing produces supported data types;
- deterministic seeds behave as expected;
- fit time, prediction time, peak memory, and artifact size are plausible;
- serialization succeeds if the family reaches packaging.

## Deliverables

- Candidate registry with unique family and pipeline identifiers.
- Baseline specifications.
- Typed, bounded, conditional search spaces.
- Compatibility matrix for tasks, feature representations, and outputs.
- Estimated resource envelope and concurrency limits.
- Preflight results and excluded-family reasons.

## Safeguards

- Exclude candidates that cannot meet hard latency, memory, licensing, interpretability, or interface requirements.
- Keep learned preprocessing and estimation in one cross-validated pipeline.
- Validate parameter combinations before consuming training resources.
- Preserve model defaults explicitly; library upgrades can change implicit defaults.

## Exit criteria

The stage is complete when every registered configuration can be sampled, validated, fit, scored, and identified unambiguously, and when no registered family violates a known hard constraint.
