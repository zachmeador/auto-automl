# Run Plan

Run ID:
Project ID:
Project root: `projects/<project_id>/`
Status: planned

## Hypothesis

Describe one experiment hypothesis.

## Expected Effect

- Primary metric:
- Expected direction:
- Minimum useful improvement:

## Baseline

- Baseline run ID:
- Baseline metric:

## Planned Changes

- Data changes:
- Feature changes:
- Model changes:
- Hyperparameter changes:
- Evaluation changes:

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
- Manifest written:
- Metrics written:
- Leakage audit written:
- Metric review written:
