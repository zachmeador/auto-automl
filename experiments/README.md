# Experiment Templates

The root `experiments/` directory contains reusable templates and framework documentation only.

Do not write task-specific run artifacts here. All task-specific experiment work belongs under `projects/<project_id>/`.

Recommended run layout:

```text
projects/<project_id>/
  experiments/
    dataset_contract.md
    split_contract.md
    metric_contract.md
    registry.jsonl
    memory.jsonl
    runs/<run_id>/
      manifest.json
      plan.md
      metrics.json
      leakage_report.json
      leakage_report.md
      metric_review.md
      notes.md
```

`manifest.json` should conform to `schemas/experiment-manifest.schema.json`.

`leakage_report.json` should conform to `schemas/leakage-report.schema.json`.

Each admitted or rejected run should append one JSON object to a project-local registry file, typically `projects/<project_id>/experiments/registry.jsonl`, conforming to `schemas/registry-record.schema.json`.

The registry is intentionally JSONL so agents and scripts can append records without rewriting a central database.

Templates for dataset, split, metric, run plan, leakage report, metric review, registry, and memory records are in `experiments/templates/`.

## Admission Rules

- `leakage_verdict` must be `PASS` for leaderboard admission.
- `metric_review_verdict` must be `PASS` for leaderboard admission.
- Runs with `WARN` may be retained for memory but should not become default model candidates without human review.
- Runs with `FAIL` must be marked rejected and distilled into "avoid" memory.
