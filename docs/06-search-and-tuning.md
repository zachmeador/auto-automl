# Search and tuning

## Goal

Evaluate candidate configurations under one fixed protocol and select a small set of finalists within a declared resource budget.

## Search specification

Freeze these inputs before the first trial:

- candidate registry and search-space version;
- dataset fingerprint and fold assignments;
- primary and secondary scorers;
- per-trial and total time, memory, and compute limits;
- maximum trial count and concurrency;
- random seeds;
- failure, retry, pruning, and stopping policies;
- ranking and tie-breaking rules.

Changing any item creates a new search run. Do not merge results from incompatible protocols without labeling the difference.

## Choose a search method

- **Grid search:** Use for a small discrete space where every combination is meaningful.
- **Random search:** Use for broad spaces where only some parameters strongly affect performance.
- **Bayesian or model-based search:** Use when trials are expensive enough to justify sequential guidance.
- **Successive halving or bandit search:** Use when performance at a smaller resource—rows, iterations, or time—predicts full-resource performance.

The method must honor conditional parameters and reproducibility requirements. Early-stopping methods must define the resource axis and promotion rule. Scikit-learn summarizes standard approaches in its [hyperparameter tuning guide](https://scikit-learn.org/stable/modules/grid_search.html).

## Trial execution

For each sampled configuration:

1. Validate parameter types, conditions, and resource estimates.
2. For each fold, construct a fresh pipeline.
3. Fit every learned preprocessing step and the estimator on the fold's training partition only.
4. Predict the validation partition and calculate all declared metrics.
5. Record fold size, score, fit time, prediction time, resource use, warnings, and failure details.
6. Aggregate fold results using the specified rule; normally retain mean, standard deviation, and individual scores.
7. Save enough metadata to reconstruct the trial. Save model artifacts only when required; metadata and predictions are often sufficient during search.

Use identical folds and scorers across configurations. Cache only deterministic computations whose cache key includes every relevant input, parameter, data version, and fold.

## Failures and pruning

Classify failures instead of converting them to an unexplained worst score:

- invalid configuration;
- numerical failure or non-convergence;
- out of memory;
- timeout;
- data incompatibility;
- infrastructure interruption;
- scorer or implementation defect.

Retry only failures likely to be transient. Retain the original attempt. For pruned trials, record the resource consumed, intermediate scores, and pruning reason; do not rank partial-resource results beside completed trials as equivalent observations.

## Ranking and stopping

Rank completed configurations by the primary validation metric. Then apply hard constraints. Use secondary criteria only as declared tie-breakers, such as lower variance, lower latency, lower complexity, or smaller artifact size.

Stop when the budget is consumed, a specified performance target is reached, improvement remains below a tolerance for a declared number of trials, or no valid trials remain. The stopping rule is evidence about the search, not proof that a global optimum was found.

## Deliverables

- Immutable search-run specification.
- Complete trial ledger with configurations, folds, scores, timing, resource use, status, warnings, and seeds.
- Ranked valid trials and Pareto views for performance versus constraints.
- Failure and pruning summary.
- Budget consumption and stopping reason.
- Small finalist set for formal evaluation.

## Safeguards

- Limit nested parallelism; concurrent trials whose estimators also use all cores can exhaust memory and reduce throughput.
- Do not choose candidates from rounded scores when differences are smaller than fold variability.
- Preserve unsuccessful trials; they define the tested space and expose systematic incompatibilities.
- Repeated optimization can overfit noisy validation scores. Evaluate the final choice independently; selection bias can rival differences between algorithms ([Cawley and Talbot, 2010](https://jmlr.org/papers/v11/cawley10a.html)).

## Exit criteria

The stage is complete when the budget terminates under a recorded rule, every attempted trial is accounted for, rankings can be reproduced from the ledger, and finalists satisfy all known hard constraints.
