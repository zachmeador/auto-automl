# Data splitting

## Goal

Create development and evaluation partitions that reproduce the independence, grouping, and time structure expected after release. Splitting is part of the problem definition, not a generic random operation.

## Partition roles

- **Training folds:** Fit model parameters and learned preprocessing.
- **Validation folds:** Compare pipelines, tune hyperparameters, choose thresholds, and make feature decisions.
- **Test set:** Estimate performance after all development choices are frozen.

The test set is used once for the formal evaluation. Any decision made from its results turns it into validation data.

## Choose the split unit

The split unit is the smallest unit allowed to cross partitions. It may differ from a row.

- Use rows only when observations are independent.
- Group by customer, patient, device, household, session, site, or source when related rows share information.
- Group near-duplicates and repeated measurements together.
- For time-dependent tasks, split at the relevant event or entity time and preserve causal order.

[`GroupKFold`](https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.GroupKFold.html) keeps each group in one fold. Stratified grouped splitting may also be needed when both group separation and class balance matter.

## Choose the split strategy

### Random or stratified

Use for exchangeable observations drawn from a stable population. Stratification stabilizes class proportions; it does not correct dataset bias or dependence.

### Grouped

Use when multiple observations share an entity or acquisition context. Balance folds by groups, not rows. Report group counts and target distribution because large groups can still create uneven folds.

### Temporal

Train on earlier observations and validate on later observations. Match the real forecast horizon and retraining pattern. Add a gap or embargo when adjacent records share features, labels, or aggregation windows. [`TimeSeriesSplit`](https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.TimeSeriesSplit.html) implements expanding-window evaluation for equally spaced observations.

### Geographic, site, or domain holdout

Hold out entire locations, institutions, acquisition systems, or domains when generalization to new domains is part of the intended use. This measures a harder and more relevant shift than random row splitting.

## Procedure

1. Freeze eligible observations before assigning partitions.
2. Reserve the test set according to the chosen unit and strategy.
3. Build cross-validation folds from the remaining data.
4. Persist row indices, group keys, splitter configuration, ordering rules, and random seeds.
5. For every partition and fold, report rows, groups, time range, target distribution, and important subgroup counts.
6. Assert that train, validation, and test indices are disjoint.
7. Assert zero prohibited group overlap and correct temporal ordering.
8. Confirm that every fold contains enough target examples to fit and score all candidate models.
9. Fit preprocessing, feature selection, resampling, calibration, and the estimator only within each training fold.

## Deliverables

- Frozen test-set indices or selection rule.
- Reusable cross-validation splitter and exact fold assignments.
- Split diagnostics and overlap assertions.
- Rationale connecting the split strategy to expected inference conditions.

## Safeguards

- Do not inspect test labels during development.
- Do not impute, scale, encode, select features, oversample, or otherwise learn from data before fold assignment. Scikit-learn documents this leakage pattern in [common pitfalls](https://scikit-learn.org/stable/common_pitfalls.html).
- Use nested evaluation or an independent test set when extensive search could overfit validation scores. Selection bias can be as large as the measured differences between algorithms ([Cawley and Talbot, 2010](https://jmlr.org/papers/v11/cawley10a.html)).
- Version split definitions with the dataset; a seed alone is insufficient if row order or membership changes.

## Exit criteria

The stage is complete when partitions reproduce deployment conditions, can be reconstructed exactly, contain adequate samples, and pass identity, group, and time-overlap checks.
