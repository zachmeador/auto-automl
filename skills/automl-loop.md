---
name: automl-loop
description: Run one fresh-context Ralph-style AutoML experiment iteration with strict evaluation, leakage-audit, metric-review, and memory-distillation gates.
---

# AutoML Loop Skill

Use this skill for one bounded AutoML iteration. Do not attempt to solve the entire project in one session.

## Inputs

Required:

- Dataset contract: source, target, prediction time, allowed features, unavailable features, entity/time semantics.
- Split contract: train/validation/test definitions, group/time constraints, split artifact hashes if available.
- Metric contract: objective metric, direction, tie-breakers, minimum practical improvement, runtime budget.
- Current registry or leaderboard.
- Prior distilled memory, if available.

Optional:

- One user-provided hypothesis.
- Existing baseline code.
- Approved model/tool list.

## Hard Rules

- Do not access sealed final holdout labels or metrics.
- Optimize validation only.
- Create or modify task-specific project code under `projects/<project_id>/`.
- Implement exactly one experiment hypothesis or one tightly related experiment family.
- Every artifact that influences future decisions must be recorded.
- A run is not admitted until leakage audit and metric review pass.

## Procedure

1. Rehydrate only relevant context.
   - Read contracts, registry, and compact memory.
   - Identify the current best admitted baseline.
   - Select one next hypothesis.

2. Resolve the project workspace.
   - If a project workspace does not exist, create `projects/<project_id>/`.
   - Keep task-specific source code, configs, notebooks, and local scripts inside that child directory.
   - Keep run metadata under `experiments/runs/<run_id>/`.

3. Write `experiments/runs/<run_id>/plan.md`.
   - State the hypothesis.
   - State expected metric movement.
   - State leakage risks before implementation.

4. Implement the experiment.
   - Keep preprocessing inside train-fold-only pipelines.
   - Use existing evaluation commands when present.
   - If no command exists, create the smallest task-local command needed and record it in the manifest.

5. Run validation.
   - Capture metrics, runtime, random seeds, data hashes, code version, and command lines.
   - Write `metrics.json` and `manifest.json`.

6. Run the gates.
   - Apply `skills/leakage-auditor.md`.
   - Apply `skills/metric-reviewer.md`.
   - Do not admit the run if either gate fails.

7. Update registry.
   - Append one structured registry record with `admitted: true` only if both gates pass.
   - Rejected runs still get registry records when they influenced future decisions.

8. Distill memory.
   - Apply `skills/experiment-distiller.md`.
   - Keep memory compact. Do not paste long logs.

## Stop Conditions

Stop after one iteration and report:

- run id
- hypothesis
- metric delta versus baseline
- leakage verdict
- metric review verdict
- admitted/rejected status
- next recommended hypothesis
