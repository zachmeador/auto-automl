# Project Workspaces

`projects/<project_id>/` is the home for task-specific ML workspaces.

The repository root is the reusable control layer: skills, schemas, docs, and templates. Child project directories are for generated training code, data adapters, configs, notebooks, data splits, project cards, frontier ledgers, model artifacts, outputs, and project-local scripts.

Recommended layout:

```text
projects/<project_id>/
  README.md
  pyproject.toml
  uv.lock
  src/
  configs/
  experiments/
    project_card.md
    frontier.jsonl
  data/
  notebooks/
  outputs/
```

The default loop state is `experiments/project_card.md` plus `experiments/frontier.jsonl`.

## Python Runtime

Python project workspaces are designed around project-local `uv` environments when Python experiment code exists.

- `pyproject.toml` describes project-local Python dependencies and scripts.
- `uv.lock` captures dependency resolution when present.
- `.venv/` and `.uv-cache/` are project-local runtime/cache directories.
- Stable evaluator commands usually live in `pyproject.toml` scripts or existing project tooling.

Final holdout data and label access are governed by the project card.
