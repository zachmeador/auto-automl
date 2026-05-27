# Portable AutoML Agent Skills

These files are plain markdown skills intended for agentic coding tools such as Codex, Claude Code, Cursor, Aider, and similar CLIs.

They are not tied to one skill runtime. A harness may pass one skill as the active instruction file, or an agent may read the relevant skill directly.

Execution, sandboxing, long-running loop scheduling, and IDE integration are responsibilities of the host agent environment. The skills here define what each AutoML loop step must do and record.

The core skills are also tooling-neutral. Do not steer users toward a specific AutoML, tracking, deployment, or cloud platform unless they ask for it or the project already uses it.

## Recommended Invocation Pattern

Use `AGENTS.md` as the entry point. It defines how to find the child project, contracts, registry, memory, loop skill, verification gates, and stop policy.

Run a fresh worker session for one iteration:

```text
Read AGENTS.md, README.md, skills/automl-loop.md, the dataset contract, the split contract, the metric contract, and the current experiment registry. If the project stop policy is not already satisfied, execute exactly one worker iteration and write the required artifacts.
```

Then run independent audit/review passes:

```text
Read skills/leakage-auditor.md and audit projects/<project_id>/experiments/runs/<run_id>/.
Read skills/metric-reviewer.md and review projects/<project_id>/experiments/runs/<run_id>/.
Read skills/experiment-distiller.md and update memory only after audit/review.
```

After the worker iteration, check the project stop policy again and report `application_loop_status` as `continue` or `stop`. The host agent environment may launch another fresh worker iteration when status is `continue`.

For Python projects, create or reuse a `pyproject.toml` in `projects/<project_id>/` and run commands from that directory with `uv --cache-dir .uv-cache run ...`. Do not run task-specific code with bare system `python`, `python3`, or `pip` from the repository root.

## Skill Files

- `automl-loop.md`: orchestrates one Ralph-style worker iteration.
- `data-profile.md`: creates dataset, split, and metric contracts.
- `feature-engineer.md`: proposes and implements fold-safe feature changes.
- `model-search.md`: proposes and implements bounded model/HPO changes.
- `leakage-auditor.md`: red-teams leakage and split integrity.
- `metric-reviewer.md`: validates objective, metric, and claimed improvement.
- `experiment-distiller.md`: summarizes runs into compact memory records.

## Extension Packs

Tool-specific skills should live outside the core set as optional packs. A Databricks + MLflow 3 pack is a good future candidate for projects that already use that stack or explicitly need deployment/model-registry guidance.
