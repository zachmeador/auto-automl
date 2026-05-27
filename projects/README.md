# Project Workspaces

Agents should create task-specific ML project code under `projects/<project_id>/`.

The repository root is the reusable control layer: skills, schemas, docs, templates, and experiment metadata. Child project directories are for generated training code, data adapters, configs, notebooks, model artifacts, and project-local scripts.

Recommended layout:

```text
projects/<project_id>/
  README.md
  src/
  configs/
  data/
  notebooks/
  outputs/
```

Keep final holdout data and labels sealed according to the split contract. Do not copy sealed final holdout labels into project workspaces during normal loop iterations.

