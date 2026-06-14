# Experiment Templates

The root `experiments/` directory contains reusable templates and framework documentation only.

Task-specific experiment workspaces live under `projects/<project_id>/`.

Default loop layout:

```text
projects/<project_id>/
  experiments/
    project_card.md
    frontier.jsonl
```

`frontier.jsonl` is a compact ledger of worker-session outcomes. Rows use `schemas/frontier-record.schema.json` when possible.

## Frontier Rules

- The frontier advances when a candidate improves the declared validation metric under the project card's comparison rule.
- The first valid baseline can advance the frontier without a prior comparison.
- Non-improving attempts can still be logged when they inform future search.
- The final holdout is never used for frontier advancement.

## Review Rules

Leakage and metric review checklists are most relevant when:

- split, evaluator, labels, joins, or data availability semantics changed
- high-risk features were added
- validation improved suspiciously
- the comparison is a close call and the project card has a close-call rule
- the candidate is being recommended to the user

Review results can be represented in the frontier row or a short project-local note. Routine search does not need a separate run-governance bundle.
