---
name: generate-ml-environment-skillpack
description: Generate a portable, environment-specific set of agent skills for training, tracking, storing, registering, deploying, and operating machine-learning models. Use when defining or onboarding an ML platform, translating between enterprise platforms such as Databricks and homelab infrastructure such as a VM plus database and object/file store, documenting an existing model lifecycle, or creating agent instructions that bind a common MLOps capability contract to concrete local tools and commands.
---

# Generate ML Environment Skillpack

Turn one declarative environment manifest into a small pack of operational skills. Preserve the same lifecycle and safety model across managed platforms and hand-assembled infrastructure.

## Workflow

1. Inspect the target repository and available infrastructure documentation. Prefer read-only discovery through existing CLIs, configuration, and platform APIs.
2. Read [references/environment-contract.md](references/environment-contract.md) completely. Use [assets/environment.example.json](assets/environment.example.json) as the starting manifest.
3. Map concrete services onto the contract. Describe unavailable capabilities explicitly; do not invent services or commands.
4. Keep credentials out of the manifest. Record only environment-variable names, secret-manager paths, workload identities, or other secret references.
5. Ask only for choices that materially change architecture or authorize access. Otherwise, use documented local conventions and label assumptions.
6. Validate before generating:

   ```bash
   python3 scripts/generate_skillpack.py validate /absolute/path/environment.json
   ```

7. Generate into a new directory:

   ```bash
   python3 scripts/generate_skillpack.py generate \
     /absolute/path/environment.json \
     --output /absolute/path/generated-skillpacks
   ```

8. Inspect every generated `SKILL.md`. Replace unknowns, verify commands against non-production or read-only targets, and keep environment-specific constraints intact.
9. Run the skill-creator validator against each generated skill before installation. Forward-test risky deployment or operations flows only in a sandbox.

## Contract rules

- Keep these capabilities distinct even when one product implements several: compute, data, metadata, artifacts, experiments, registry, serving, observability, identity, and network.
- Default tabular snapshots to Apache Parquet with explicit schemas and stable compression. Preserve immutable upstream files in their original format, then record the raw-to-Parquet derivation and fingerprints for both. Use another working format only when the environment requires it and document why.
- Treat the model manifest as the handoff between training, registry, deployment, and rollback.
- Require immutable model versions, artifact checksums, data/code provenance, and conformance fixtures.
- Separate build, release, and production mutation. A deployment request does not imply approval to deploy.
- Give homelab environments the same lifecycle guarantees as enterprise platforms. Simpler components are acceptable; missing lineage, backups, access control, or monitoring are not silently acceptable.
- Make bespoke observability concrete: log locations, metric sink, health checks, alert routes, retention, and the command used to inspect each signal.
- Never execute command templates during generation. Generated agents must substitute variables deliberately and show mutating commands before running them when approval is required.

## Output

The generator creates a normalized `environment.json` and six independent skills:

- `<environment>-ml-context`: inventory, routing, identity, and safety boundaries.
- `<environment>-train-model`: reproducible training and run submission.
- `<environment>-track-experiments`: runs, parameters, metrics, logs, and lineage.
- `<environment>-manage-models`: artifacts, manifests, registry, promotion, and rollback.
- `<environment>-deploy-model`: release validation and batch or online deployment.
- `<environment>-operate-models`: service health, logs, metrics, alerts, drift, and incidents.

Install the entire generated `skills/` directory when one agent needs the full lifecycle, or install only the relevant skills for narrower agents.

## Quality bar

Reject or revise a pack when it embeds secrets, collapses mutable aliases into model identity, omits rollback, treats a file path as sufficient provenance, claims monitoring without inspectable signals, or contains commands that are not grounded in the target environment.
