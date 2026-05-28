# Run Notes

Run ID:
Project ID:
Project root: `projects/<project_id>/`
Status: planned

## Session Objective

Describe the practical next move: baseline, debugging, model search, feature search, calibration, evaluation cleanup, or promotion.

## Hypothesis

State the hypothesis if this session is testing one.

## Baseline

- Baseline run ID:
- Baseline metric:

## Planned Changes

- Data changes:
- Feature changes:
- Model changes:
- Hyperparameter changes:
- Evaluation changes:

## Inner Search Plan

- Inner search type:
- Search space:
- Budget:
- Selection rule:
- Summary to record:

## Leakage Risks

- Split risk:
- Target leakage risk:
- Temporal leakage risk:
- Entity leakage risk:
- Preprocessing leakage risk:
- Cache/artifact risk:

## Validation Command

Run from `projects/<project_id>/` with `uv --cache-dir .uv-cache run ...` for Python projects.

```text
<command>
```

## Stop Criteria

- Validation completes:
- Candidate promoted:
- Manifest written if promoted:
- Metrics written if promoted:
- Leakage audit written if admitted:
- Metric review written if admitted:
