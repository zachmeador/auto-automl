# Portable AutoML Agent Skills

These files are plain markdown skills intended for agentic coding tools such as Codex, Claude Code, Cursor, Aider, and similar CLIs.

They are not tied to one skill runtime. A harness may pass one skill as the active instruction file, or an agent may read the relevant skill directly.

Execution, sandboxing, long-running loop scheduling, and IDE integration are responsibilities of the host agent environment. The skills here define how to keep the AutoML loop bounded, comparable, and reproducible.

## Instruction Entrypoint

`AGENTS.md` is the operational entrypoint. It explains how to find the child project, project card, frontier ledger, loop skill, review checklists, and stop policy.

## Skill Files

- `automl-loop.md`: orchestrates one Ralph-style worker session.
- `data-profile.md`: creates the project card.
- `feature-engineer.md`: proposes and implements fold-safe feature changes.
- `model-search.md`: proposes and implements bounded model/HPO changes.
- `leakage-auditor.md`: checks leakage and split integrity when risk changes.
- `metric-reviewer.md`: checks evaluator correctness and close metric calls.

## Extension Packs

Tool-specific skills should live outside the core set as optional packs.
