# Evaluation and selection

## Goal

Choose one deployable configuration using development results, then estimate its performance on untouched data. Evaluation characterizes behavior, uncertainty, and limits; it does not merely report one score.

## Select the finalist before test evaluation

Review leading validation results for:

- primary metric and fold-level dispersion;
- failures, convergence warnings, and sensitivity to seeds;
- generalization gap between training and validation;
- latency, memory, throughput, and artifact size;
- calibration or threshold behavior where relevant;
- performance across time, source, and important subgroups;
- complexity and operational dependencies;
- distance from search-space boundaries.

Choose one configuration using validation evidence only. Apply hard constraints first, then the declared ranking and tie-break rules. Record why it won and why close alternatives did not. If uncertainty between finalists matters, resolve it with additional development-only evaluation—not the test set.

## Formal test evaluation

1. Freeze preprocessing, model family, hyperparameters, class ordering, and threshold policy.
2. Fit the frozen pipeline on all development data allowed by the protocol.
3. Generate test predictions once and store them with stable row identifiers.
4. Compute the primary metric exactly as specified in the problem definition.
5. Compare against the trivial baseline, incumbent, acceptance threshold, and validation estimate.
6. Report sample count, metric uncertainty where practical, and the difference between test and validation performance.

Use confidence intervals or resampling units that respect the data structure. Row-level bootstrap intervals are misleading when rows are correlated by entity, group, or time.

## Required diagnostic views

Choose views relevant to the task and risk:

### Classification

- confusion matrix at the operating threshold;
- per-class precision, recall, and support;
- ranking metric when ordering matters;
- probability calibration and proper scoring rule when probabilities drive decisions;
- metric versus threshold and capacity or cost consequences.

Probability discrimination does not establish reliability. Calibration should be checked separately ([scikit-learn: probability calibration](https://scikit-learn.org/stable/modules/calibration.html)).

### Regression

- absolute and squared error summaries;
- residuals versus prediction, target magnitude, and important features;
- systematic overprediction or underprediction;
- tail errors and domain-specific tolerances;
- interval coverage when uncertainty intervals are produced.

### All tasks

- performance by time, source, geography, and relevant subgroups;
- error examples, including high-confidence failures;
- missingness and unseen-category slices;
- inference latency distribution, memory, and batch-size behavior;
- robustness to valid boundary conditions;
- comparison with declared constraints.

Model inspection may explain reliance, not causal effect. Calculate permutation importance only after establishing held-out performance; it is conditional on the fitted model, dataset, and scorer ([scikit-learn: permutation importance](https://scikit-learn.org/stable/modules/permutation_importance.html)).

## Decision outcomes

- **Accept:** All hard thresholds pass and residual risks are documented.
- **Reject:** A hard requirement fails or the model does not beat the required baseline.
- **Conditional accept:** Only when the problem definition permits a specific mitigation, such as human review or restricted scope.
- **Return to development:** A new hypothesis is worth testing. Test results may motivate it, but the existing test set cannot provide the next unbiased final estimate.

## Deliverables

- Frozen selected configuration and selection rationale.
- Test predictions and evaluation report.
- Uncertainty, subgroup, robustness, calibration, and operational results as applicable.
- Baseline and acceptance-threshold comparison.
- Accept/reject decision, limitations, and unresolved risks.

## Safeguards

- Never revise a feature, model, threshold, or metric and continue calling the same data a test set.
- Do not hide weak slices behind an aggregate metric.
- Do not claim equivalence from overlapping confidence intervals or a small observed difference without an appropriate test or tolerance.
- Keep evaluation predictions and scoring code versioned so reported numbers can be recomputed.

## Exit criteria

The stage is complete when one immutable configuration has a reproducible independent evaluation, every hard requirement has an explicit result, and the acceptance decision and limitations are recorded.
