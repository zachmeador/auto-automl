---
name: collect-local-dataset
description: Find datasets online and add them to this project's local, uncommitted dataset collection under ./data. Use when asked to get, download, import, list, inspect, or verify a public or authorized dataset for local work, such as "get the Titanic dataset and add it to the collection."
---

# Collect Local Dataset

Keep user datasets under `./data/`; this directory is intentionally excluded from version control. Store each dataset at `./data/datasets/<dataset-id>/` with original downloaded files in `source/` and provenance plus checksums in `dataset.json`. Include a `description` containing one sentence that explains what the dataset is.

## Add a dataset

1. Work from the repository root. Confirm `./data/` is ignored by Git.
2. Search online for the requested dataset. Prefer the original publisher, official repository, or established dataset registry over an unverified mirror.
3. Inspect the source page before downloading. Record the exact download URL, dataset name, a one-sentence description of what the dataset is, retrieval time, and stated license. If the license is not stated, record `unknown`; do not guess.
4. Check whether the collection already contains the dataset:

   ```bash
   python3 .agents/skills/collect-local-dataset/scripts/datasets.py list
   ```

5. Prepare a new dataset directory. Use a short stable identifier:

   ```bash
   python3 .agents/skills/collect-local-dataset/scripts/datasets.py prepare "Titanic"
   ```

6. Download the original file into the printed `source/` directory. Write to a `.part` file first and rename it only after a successful download. Preserve the publisher's filename and archive; do not clean or transform the source file in place.
7. Register the completed download:

   ```bash
   python3 .agents/skills/collect-local-dataset/scripts/datasets.py register titanic \
     --name "Titanic" \
     --source-url "https://publisher.example/data.csv" \
     --license "license stated by publisher" \
     --description "Passenger records from the Titanic disaster used for survival prediction."
   ```

8. Verify stored file checksums:

   ```bash
   python3 .agents/skills/collect-local-dataset/scripts/datasets.py verify titanic
   ```

9. Report the local path, source, license status, filenames, sizes, and checksum-verification result. Mention any authentication, terms-of-use, or provenance caveats.

Do not commit anything under `./data/`. Do not bypass access controls, accept restricted terms for the user, fabricate a license, or replace an existing dataset directory. If a source requires user authentication or acceptance, stop at that boundary and tell the user what they need to do.

## Manage the collection

List registered datasets:

```bash
python3 .agents/skills/collect-local-dataset/scripts/datasets.py list
```

Show one manifest:

```bash
python3 .agents/skills/collect-local-dataset/scripts/datasets.py show titanic
```

Verify that stored files still match their registered checksums:

```bash
python3 .agents/skills/collect-local-dataset/scripts/datasets.py verify titanic
```

Treat `source/` as immutable after registration. Put later transformations elsewhere under the dataset directory and document them in the modeling workflow; this skill manages acquisition provenance, not cleaning or feature engineering.
