---
name: sample-data-init
description: Initialize a reproducible local suite of small, medium, wide, and multi-million-row tabular datasets for testing ML ingestion, validation, preprocessing, splitting, training, and packaging workflows. Use when an agent needs Titanic or representative classification, regression, multiclass, temporal, scaling, missing-data, or mixed-type fixtures in a repository.
---

# Initialize Sample ML Data

Create a local test-data suite while following the ML environment contract's raw-data, Parquet, provenance, and validation rules.

## Workflow

1. Read repository guidance and locate its local-data directory. Default to `<repo>/data/`. Never place user data in tracked source directories.
2. Confirm the data directory is Git-ignored before downloading. Add an ignore rule only when repository guidance permits edits; otherwise stop and explain the risk.
3. Read [references/datasets.json](references/datasets.json). Use its one-sentence descriptions, pinned URLs, raw SHA-256 hashes, shapes, targets, and leakage notes instead of rediscovering substitutes.
4. Run the deterministic initializer from the repository root:

   ```bash
   uv run --no-project --with pandas --with pyarrow \
     python /absolute/path/to/sample-data-init/scripts/init_sample_data.py \
     --repo-root "$PWD"
   ```

5. Preserve downloads unchanged under `data/raw/`. Stop on a raw checksum mismatch; never silently replace or repair a source file.
6. Use `data/parquet/` as the default training input. Convert non-Parquet sources with Zstandard compression and copy upstream Parquet there unchanged for a uniform entry point.
7. Inspect `data/catalog.json`, verify that every dataset has a one-sentence `description` and that every Parquet row and column count matches, then report paths, descriptions, shapes, task types, and total disk use.
8. Call out prediction-time leakage and split constraints before recommending a target. Dataset size does not establish representativeness.

## Dataset roles

- Use Titanic for fast mixed-type, missing-value, and leakage tests.
- Use Adult for medium binary classification, imbalance, and subgroup-audit plumbing.
- Use California Housing for regression and geographic splitting.
- Use Covertype for multiclass, wider tables, and memory pressure.
- Use NYC Yellow Taxi January 2023 for a 3,066,766-row Parquet and chronological pipeline testing.

## Operating rules

- Treat raw downloads as immutable source artifacts.
- Fingerprint raw and derived files independently in `data/catalog.json`.
- Store a one-sentence `description` explaining what each dataset is in both the pinned manifest and generated catalog.
- Prefer Parquet for tabular working snapshots unless the environment contract explicitly records another requirement.
- Do not commit `data/`, credentials, caches, or temporary download files.
- Do not claim successful initialization until hashes, file signatures, and Parquet metadata validate.
- Preserve any existing valid dataset. The initializer is idempotent and must fail rather than overwrite conflicting content.
