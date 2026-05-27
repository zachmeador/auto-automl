---
name: data-profile
description: Create dataset, split, and metric contracts before AutoML experiments begin.
---

# Data Profile Skill

Use this skill before model search or feature engineering. Its output defines what the AutoML loop is allowed to optimize.

## Outputs

Write contracts as markdown or JSON under the project location chosen by the user or harness. Recommended names:

- `experiments/dataset_contract.md`
- `experiments/split_contract.md`
- `experiments/metric_contract.md`

## Dataset Contract Checklist

Record:

- target column and task type
- prediction-time meaning of one row
- allowed input columns
- explicitly forbidden columns
- timestamp column and prediction horizon, if any
- entity/group identifier, if any
- known duplicate semantics
- missing-value semantics
- label generation process, if known
- deployment setting and data availability constraints

## Split Contract Checklist

Record:

- train/validation/test split method
- exact split artifact paths or generation command
- random seed or deterministic split rule
- group isolation rule, if any
- temporal ordering rule, if any
- final holdout location and access policy
- split hashes when available

## Metric Contract Checklist

Record:

- primary metric
- maximize/minimize direction
- secondary tie-breakers
- baseline metric
- minimum practical improvement threshold
- repeated-seed or confidence interval requirement
- runtime/memory/inference constraints
- fairness, calibration, recall-at-precision, or cost constraints if relevant

## Required Warnings

If any of these are unknown, mark the contract incomplete and block model search:

- target definition
- prediction-time data availability
- split semantics
- primary metric
- final holdout policy

