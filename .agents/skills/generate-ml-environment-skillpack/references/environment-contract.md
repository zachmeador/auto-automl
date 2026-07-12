# ML environment contract

## Purpose

Describe an ML platform by capability rather than vendor. A managed platform may satisfy several capabilities with one service; a homelab may use one component per capability. The generated skills depend on the contract, not on a particular product.

## Manifest shape

The manifest is JSON with `schema_version: 1`. Required top-level keys are `environment`, `capabilities`, and `policies`.

### `environment`

- `name`: Stable human-readable environment name.
- `slug`: Optional lowercase identifier. The generator derives one when omitted.
- `class`: `managed`, `cloud`, `on-prem`, `homelab`, or another honest descriptor.
- `owner`: Responsible team or person.
- `description`: Short scope statement.

### `capabilities`

Include every capability below. Use `available: false` plus `notes` when absent. A capability may contain `provider`, `endpoint`, `uri`, `workspace`, and `commands`. Commands are inert templates and may use braces such as `{run_id}` or `{model_version}`.

- `compute`: Training execution, scheduler, queues, accelerators, runtime image, working directory, and submit/status/cancel/log commands.
- `data`: Source and derived data locations, snapshot/version mechanism, access mode, working format, and validation command. Prefer Apache Parquet for tabular snapshots. Preserve immutable upstream files separately, and fingerprint both raw and derived data.
- `metadata`: Structured store for datasets, runs, releases, ownership, and audit records.
- `artifacts`: Immutable object/file storage, URI convention, checksum algorithm, retention, and replication or backup.
- `experiments`: Tracking backend, tracking URI, run naming, lineage fields, and query/UI instructions.
- `registry`: Model identity/version scheme, aliases or stages, promotion mechanism, and rollback lookup.
- `serving`: Batch and/or online targets, packaging format, release command, health check, rollback command, and traffic policy.
- `observability`: Logs, metrics, traces, dashboards, alerts, drift signals, retention, and inspection commands. For bespoke stacks, name each concrete sink and path.
- `identity`: Human and workload authentication, authorization boundary, and `secret_refs`. Store references only, never values.
- `network`: Reachability, DNS, ingress/egress, TLS, private network assumptions, and prohibited paths.

### `policies`

- `environments`: Lifecycle environments such as development, staging, and production.
- `approval_gates`: Actions needing human or external approval.
- `data_rules`: Sensitive-data and residency constraints.
- `retention`: Minimum retention by records or artifact class.
- `recovery`: Backup, restore, RPO/RTO, and rollback expectations.
- `cost_controls`: Budgets, quotas, instance limits, or shutdown rules.

### Optional `conventions`

Record repository locations, model naming, version format, required tags, model manifest location, conformance-test command, and release-record location.

## Capability mapping examples

| Capability | Managed platform example | Homelab example |
| --- | --- | --- |
| Compute | Databricks Jobs | systemd-triggered runner or container on a GPU VM |
| Data | Delta tables | PostgreSQL plus versioned Parquet snapshots |
| Metadata | Unity Catalog/system tables | PostgreSQL schemas |
| Artifacts | Managed volumes/object storage | MinIO, NAS, or append-only filesystem path |
| Experiments | MLflow tracking | Self-hosted MLflow with PostgreSQL and MinIO |
| Registry | Managed MLflow registry | Self-hosted MLflow registry or explicit DB records |
| Serving | Model Serving | container plus systemd, Nomad, or k3s |
| Observability | platform metrics/logs | Prometheus, Grafana, Loki/journald, Alertmanager |
| Identity | workspace identity/secret scope | SSH/OIDC, service account, environment secret refs |

These are examples, not defaults. Use only components verified in the target environment.

## Minimum viable platform

A small environment can be sound with one VM, one structured database, and one durable artifact store when it also provides:

- repeatable isolated training runtimes;
- immutable data and artifact identifiers;
- structured run and release metadata;
- checksum and provenance verification;
- controlled service identity and secret injection;
- deployment health checks and rollback;
- inspectable logs and basic resource/service metrics;
- backup and restore procedures.

Call missing guarantees out as gaps with an owner and proposed remediation. Do not conceal them behind a product label.

## Discovery checklist

1. Identify repository and runtime conventions.
2. Inventory existing CLIs, config files, service endpoints, and identity mechanisms without revealing secrets.
3. Trace one model from data snapshot through training run, artifact, registry record, deployment, logs, and rollback.
4. Classify commands as read-only, build, release, or production mutation.
5. Verify the observability path from model request or batch job to logs, metrics, alerts, and retention.
6. Record unknowns and stop before unauthorized external changes.
