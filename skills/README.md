# Portable AutoML Agent Skills

These files are plain markdown skills intended for agentic coding tools such as Codex, Claude Code, Cursor, Aider, and similar CLIs.

They are not tied to one skill runtime. A harness may pass one skill as the active instruction file, or an agent may read the relevant skill directly.

Execution, sandboxing, long-running loop scheduling, and IDE integration are responsibilities of the host agent environment. The skills here define what each AutoML loop step must do and record.

The core skills are also tooling-neutral. Do not steer users toward a specific AutoML, tracking, deployment, or cloud platform unless they ask for it or the project already uses it.

## Recommended Invocation Pattern

Run a fresh agent session for one iteration:

```text
Read AGENTS.md, README.md, skills/automl-loop.md, the dataset contract, the split contract, the metric contract, and the current experiment registry. Execute exactly one experiment iteration and write the required artifacts.
```

Then run independent audit/review passes:

```text
Read skills/leakage-auditor.md and audit experiments/runs/<run_id>/.
Read skills/metric-reviewer.md and review experiments/runs/<run_id>/.
Read skills/experiment-distiller.md and update memory only after audit/review.
```

## Skill Files

- `automl-loop.md`: orchestrates one Ralph-style experiment iteration.
- `data-profile.md`: creates dataset, split, and metric contracts.
- `feature-engineer.md`: proposes and implements fold-safe feature changes.
- `model-search.md`: proposes and implements bounded model/HPO changes.
- `leakage-auditor.md`: red-teams leakage and split integrity.
- `metric-reviewer.md`: validates objective, metric, and claimed improvement.
- `experiment-distiller.md`: summarizes runs into compact memory records.

## Extension Packs

Tool-specific skills should live outside the core set as optional packs. A Databricks + MLflow 3 pack is a good future candidate for projects that already use that stack or explicitly need deployment/model-registry guidance.
