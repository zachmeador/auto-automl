---
name: leakage-auditor
description: Red-team one AutoML run for train/eval/test leakage, target leakage, temporal leakage, group leakage, and final-holdout misuse.
---

# Leakage Auditor Skill

Use this skill after an experiment run and before leaderboard admission. Be adversarial. The default posture is that a surprising metric improvement is suspicious until explained.

## Inputs

- Dataset contract
- Split contract
- Run plan
- Experiment code or diff
- Manifest
- Metrics
- Feature list
- Any cached artifacts touched by the run

## Verdicts

- `PASS`: no blocking leakage found.
- `WARN`: no confirmed leakage, but evidence is incomplete or risk remains.
- `FAIL`: confirmed or highly likely leakage; run cannot be admitted.

## Audit Checklist

Split integrity:

- Are train, validation, and test boundaries explicit?
- Are split artifact hashes recorded?
- Did any code regenerate splits inconsistently?
- Are groups isolated when required?
- Are time splits chronological when required?

Final holdout:

- Did any loop step read final holdout labels or metrics?
- Did any code path train, tune, select, calibrate, threshold, or early-stop using final holdout data?
- Was final holdout used more than once or used before model selection stopped?

Preprocessing:

- Are imputers, scalers, encoders, feature selectors, PCA, vectorizers, oversamplers, and target encoders fit only on training folds?
- Are validation/test rows transformed with fitted training objects only?
- Are caches keyed by split and fold?

Target leakage:

- Do features encode the label directly or indirectly?
- Are post-outcome columns, future statuses, or label-generation artifacts present?
- Are target encodings nested inside training folds?

Temporal leakage:

- Do rolling windows exclude the current/future target period?
- Are timestamp availability and prediction horizon explicit?
- Are lag features shifted correctly?

Entity leakage:

- Can duplicate or near-duplicate entities cross split boundaries?
- Are household/user/customer/device/patient/order family relations handled?

Metric/selection leakage:

- Has repeated validation probing effectively turned validation into training?
- Was the metric chosen after seeing results?
- Were failed experiments hidden from the registry?

## Output

Write `leakage_report.json` conforming to `schemas/leakage-report.schema.json`, plus a human-readable `leakage_report.md`.

Required fields:

- `verdict`
- `blocking_findings`
- `warnings`
- `checks_performed`
- `evidence`
- `required_fixes`

If verdict is `FAIL`, include the shortest concrete fix path.

