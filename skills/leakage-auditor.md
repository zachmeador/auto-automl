---
name: leakage-auditor
description: Check AutoML setup changes, high-risk experiments, or final candidates for train/eval/test leakage, target leakage, temporal leakage, group leakage, and final-holdout misuse.
---

# Leakage Auditor Skill

Use this checklist when leakage risk can change the meaning of validation results. It is not required for every routine frontier iteration.

Use it for:

- initial split/evaluator setup
- changes to split generation, evaluator code, data joins, caches, or label construction
- high-risk feature families such as target encodings, aggregates, lags, text/vector features, or identifiers
- suspicious validation improvements
- final or user-recommended candidates

## Inputs

- Project card
- Frontier record or run notes
- Experiment code or diff
- Metrics
- Feature list, if relevant
- Any cached artifacts touched by the run

All inspected task-specific artifacts should be under `projects/<project_id>/`.

## Verdicts

- `PASS`: no blocking leakage found.
- `WARN`: no confirmed leakage, but evidence is incomplete or risk remains.
- `FAIL`: confirmed or highly likely leakage; the candidate cannot be recommended or used as the frontier until fixed.

## Checklist

Split integrity:

- Are train, validation, and final holdout boundaries explicit?
- Did any code regenerate splits inconsistently?
- Are groups isolated when required?
- Are time splits chronological when required?

Final holdout:

- Did any loop step read final holdout labels or metrics?
- Did any code path train, tune, select, calibrate, threshold, or early-stop using final holdout data?
- Was final holdout used before model selection stopped?

Preprocessing:

- Are imputers, scalers, encoders, feature selectors, PCA, vectorizers, oversamplers, and target encoders fit only on training folds?
- Are validation/test rows transformed with fitted training objects only?
- Are caches keyed by split and fold when learned preprocessing is cached?

Target leakage:

- Do features encode the label directly or indirectly?
- Are post-outcome columns, future statuses, or label-generation artifacts present?
- Are target encodings nested inside training folds?

Temporal leakage:

- Do rolling windows exclude the current/future target period?
- Are timestamp availability and prediction horizon explicit when time matters?
- Are lag features shifted correctly?

Entity leakage:

- Can duplicate or near-duplicate entities cross split boundaries?
- Are household/user/customer/device/patient/order family relations handled when relevant?

Validation probing:

- Is the loop tracking validation probes or run attempts in the frontier ledger?
- Is model selection still using only validation, with final holdout sealed?

## Output

Write a short verdict in the frontier record or a short project-local note:

- verdict
- blocking findings
- warnings
- evidence
- required fixes
