# Project Workspaces

Agents should create all task-specific ML work under `projects/<project_id>/`.

The repository root is the reusable control layer: skills, schemas, docs, and templates. Child project directories are for generated training code, data adapters, configs, notebooks, data splits, experiment records, model artifacts, outputs, and project-local scripts.

Recommended layout:

```text
projects/<project_id>/
  README.md
  pyproject.toml
  uv.lock
  src/
  configs/
  experiments/
  data/
  notebooks/
  outputs/
```

## Python Runtime

Python projects should use project-local `uv`.

- Create or reuse `pyproject.toml` in the child project.
- Run commands from `projects/<project_id>/`.
- Use `uv --cache-dir .uv-cache run <command>`.
- Prefer `pyproject.toml` scripts for repeated commands.
- Do not call bare `python`, `python3`, or `pip` from the repository root for task-specific work.
- Keep `.venv/`, `.uv-cache/`, and `uv.lock` inside the child project.

Keep final holdout data and labels sealed according to the split contract. Do not copy sealed final holdout labels into project workspaces during normal loop iterations.
