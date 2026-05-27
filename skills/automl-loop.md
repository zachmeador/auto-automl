---
name: automl-loop
description: Run one fresh-context Ralph-style AutoML experiment iteration with strict evaluation, leakage-audit, metric-review, and memory-distillation gates.
---

# AutoML Worker Iteration Skill

Use this skill for one bounded worker iteration inside the larger AutoML application loop. A worker iteration is not the whole project unless the metric contract's stop policy says the project is done.

## Terminology

`Worker iteration` means one fresh-context Ralph worker invocation. It does not forbid bounded inner algorithmic loops.

Allowed inner loops include cross-validation, hyperparameter search, threshold search, feature selection, ablations, repeated seeds, and model-family searches when they are part of the declared experiment hypothesis.

Inner loops must:

- stay within the metric contract's runtime/cost/search budget
- use only approved train/validation data
- keep the final holdout sealed
- record every trial or a reproducible search summary
- report the selected candidate and selection criterion
- remain narrow enough to be audited as one experiment family

## Inputs

Required:

- Dataset contract: source, target, prediction time, allowed features, unavailable features, entity/time semantics.
- Split contract: train/validation/test definitions, group/time constraints, split artifact hashes if available.
- Metric contract: objective metric, direction, project goal, stop policy, tie-breakers, minimum practical improvement, runtime budget.
- Current registry or leaderboard.
- Prior distilled memory, if available.

Optional:

- One user-provided hypothesis.
- Existing baseline code.
- Approved model/tool list.

## Hard Rules

- Do not access sealed final holdout labels or metrics.
- Optimize validation only.
- Keep all task-specific work under `projects/<project_id>/`.
- Do not write project-specific code, contracts, data, outputs, run records, registries, or memory files at the repository root or under root-level `experiments/runs/`.
- Implement exactly one experiment hypothesis or one tightly related experiment family.
- You may run a bounded inner search inside that experiment family when the search space is defined before execution and fully recorded.
- Every artifact that influences future decisions must be recorded.
- A run is not admitted until leakage audit and metric review pass.

## Python Runtime Rules

For Python experiments:

- Create or reuse `projects/<project_id>/pyproject.toml`.
- Run commands from `projects/<project_id>/`.
- Use `uv --cache-dir .uv-cache run <command>` instead of bare `python`, `python3`, `pip`, or a global environment.
- Prefer `[project.scripts]` entries in `pyproject.toml` for repeatable prepare/train/evaluate/audit commands.
- Keep `uv.lock`, `.venv/`, and `.uv-cache/` inside `projects/<project_id>/`.
- Record each command and repo-relative project working directory, for example `projects/<project_id>`, in the manifest.

## Procedure

1. Rehydrate only relevant context.
   - Read contracts, registry, and compact memory.
   - Check whether the project stop policy is already satisfied before starting a new experiment.
   - Identify the current best admitted baseline.
   - Select one next hypothesis.

2. Resolve the project workspace.
   - If a project workspace does not exist, create `projects/<project_id>/`.
   - Keep task-specific source code, configs, notebooks, data, outputs, contracts, registries, memory, and local scripts inside that child directory.
   - Keep run metadata under `projects/<project_id>/experiments/runs/<run_id>/`.
   - For Python projects, set up or reuse the project-local `uv` environment before running project code.

3. Write `projects/<project_id>/experiments/runs/<run_id>/plan.md`.
   - State the hypothesis.
   - State expected metric movement.
   - State leakage risks before implementation.

4. Implement the experiment.
   - Keep preprocessing inside train-fold-only pipelines.
   - Use existing evaluation commands when present.
   - If no command exists, create the smallest task-local command needed under `projects/<project_id>/` and record it in the manifest.

5. Run validation.
   - Capture metrics, runtime, random seeds, data hashes, code version, and command lines.
   - Write `metrics.json` and `manifest.json`.

6. Run the gates.
   - Apply `skills/leakage-auditor.md`.
   - Apply `skills/metric-reviewer.md`.
   - Do not admit the run if either gate fails.

7. Update registry.
   - Append one structured registry record with `admitted: true` only if both gates pass.
   - Write the registry under `projects/<project_id>/experiments/registry.jsonl`.
   - Rejected runs still get registry records when they influenced future decisions.

8. Distill memory.
   - Apply `skills/experiment-distiller.md`.
   - Keep memory compact. Do not paste long logs.

9. Check project-level stop policy.
   - Read `projects/<project_id>/experiments/metric_contract.md`.
   - Report whether a stop condition is satisfied.
   - If no stop condition is satisfied, report that the application loop should continue and include the next recommended hypothesis.
   - If a stop condition is satisfied, report the stopping reason and current best admitted run.

## Worker Stop Conditions

The worker iteration stops after one bounded experiment and reports:

- run id
- hypothesis
- metric delta versus baseline
- leakage verdict
- metric review verdict
- admitted/rejected status
- project stop condition status
- application loop status: `continue` or `stop`
- next recommended hypothesis

Do not claim "AutoML complete" unless the project-level stop policy is satisfied.
