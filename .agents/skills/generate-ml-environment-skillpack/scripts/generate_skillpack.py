#!/usr/bin/env python3
"""Validate an ML environment manifest and generate environment-bound agent skills."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any


CAPABILITIES = (
    "compute",
    "data",
    "metadata",
    "artifacts",
    "experiments",
    "registry",
    "serving",
    "observability",
    "identity",
    "network",
)

SKILLS = {
    "ml-context": (
        "ML Platform Context",
        "Use for ML platform inventory, routing, identity, safety boundaries, and deciding which environment capability handles a task.",
        ("identity", "network", "compute", "data", "metadata", "artifacts", "experiments", "registry", "serving", "observability"),
        "Inventory before acting. Resolve the target lifecycle environment, identity, network boundary, and approval gate. Route work to the concrete capability recorded below. Do not expose secret values or treat reachability as authorization.",
    ),
    "train-model": (
        "Train Models",
        "Use for reproducible model training, data snapshot validation, run submission, status, cancellation, and training logs.",
        ("compute", "data", "metadata", "experiments", "artifacts", "identity", "network"),
        "Freeze the run specification before submission: code revision, data fingerprint, runtime digest, parameters, seeds, resources, and owner. Validate inputs, submit through the recorded compute interface, capture the run identifier, and link logs and artifacts. Never silently retry with changed inputs.",
    ),
    "track-experiments": (
        "Track Experiments",
        "Use for experiment runs, parameters, metrics, logs, lineage, comparisons, and reproducibility records.",
        ("experiments", "metadata", "data", "artifacts", "compute", "identity"),
        "Create or query structured run records. Every comparable run must link code revision, data fingerprint, runtime, complete parameters, seeds, metrics, artifacts, and owner. Distinguish exploratory metrics from approved evaluation evidence.",
    ),
    "manage-models": (
        "Manage Model Artifacts",
        "Use for model packaging, checksums, manifests, registry versions, promotion, provenance, retention, and rollback selection.",
        ("artifacts", "registry", "metadata", "experiments", "data", "identity"),
        "Identify models by immutable version and artifact checksum; treat aliases and stages only as mutable pointers. Require a model manifest, provenance, evaluation decision, input/output schema, conformance fixtures, dependency lock, and rollback target before promotion. Promotion is a release action and may require approval.",
    ),
    "deploy-model": (
        "Deploy Models",
        "Use for validating and releasing model versions to batch or online serving targets, health checks, traffic changes, and rollback.",
        ("serving", "registry", "artifacts", "observability", "identity", "network"),
        "Resolve an immutable approved model version. Run clean-load and conformance tests in a target-like runtime, verify the release manifest and rollback target, then show the release plan and observe approval gates. After release, verify health, prediction fixtures, logs, metrics, and traffic before declaring success.",
    ),
    "operate-models": (
        "Operate Models",
        "Use for deployed-model health, logs, metrics, alerts, drift, incidents, capacity, backups, and rollback diagnosis.",
        ("observability", "serving", "metadata", "registry", "artifacts", "compute", "identity", "network"),
        "Start with read-only inspection: release identity, health, recent changes, logs, metrics, alerts, traffic, dependencies, and drift signals. Correlate by run and release identifiers. Separate mitigation from root cause; do not restart, scale, roll back, or mutate production without applicable authorization. Record incident evidence and follow-up gaps.",
    ),
}


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug[:40] or "ml-environment"


def load_manifest(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"cannot read valid JSON from {path}: {exc}") from exc
    if not isinstance(data, dict):
        raise ValueError("manifest root must be an object")
    return data


def validate(data: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if data.get("schema_version") != 1:
        errors.append("schema_version must be 1")
    environment = data.get("environment")
    if not isinstance(environment, dict):
        errors.append("environment must be an object")
    elif not isinstance(environment.get("name"), str) or not environment["name"].strip():
        errors.append("environment.name must be a non-empty string")
    capabilities = data.get("capabilities")
    if not isinstance(capabilities, dict):
        errors.append("capabilities must be an object")
    else:
        for name in CAPABILITIES:
            capability = capabilities.get(name)
            if not isinstance(capability, dict):
                errors.append(f"capabilities.{name} must be an object")
            elif "available" not in capability or not isinstance(capability["available"], bool):
                errors.append(f"capabilities.{name}.available must be true or false")
            elif capability["available"] is False and not capability.get("notes"):
                errors.append(f"capabilities.{name}.notes must explain an unavailable capability")
    if not isinstance(data.get("policies"), dict):
        errors.append("policies must be an object")
    for path, value in walk(data):
        key = path[-1].lower() if path else ""
        if key in {"password", "secret", "token", "api_key", "private_key", "access_key"}:
            errors.append(f"{'.'.join(path)} looks like a secret value; use identity.secret_refs")
        if isinstance(value, str) and "-----BEGIN " in value:
            errors.append(f"{'.'.join(path)} appears to contain private key material")
    return errors


def walk(value: Any, path: tuple[str, ...] = ()):
    if isinstance(value, dict):
        for key, child in value.items():
            yield from walk(child, path + (str(key),))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from walk(child, path + (str(index),))
    else:
        yield path, value


def yaml_quote(value: str) -> str:
    return '"' + value.replace("\\", "\\\\").replace('"', '\\"') + '"'


def capability_section(name: str, value: dict[str, Any]) -> str:
    body = json.dumps(value, indent=2, sort_keys=True)
    return f"### {name}\n\n```json\n{body}\n```"


def make_skill(
    skill_name: str,
    display_name: str,
    trigger: str,
    capability_names: tuple[str, ...],
    procedure: str,
    data: dict[str, Any],
) -> tuple[str, str]:
    env = data["environment"]
    policies = json.dumps(data["policies"], indent=2, sort_keys=True)
    conventions = json.dumps(data.get("conventions", {}), indent=2, sort_keys=True)
    sections = "\n\n".join(
        capability_section(name, data["capabilities"][name]) for name in capability_names
    )
    description = f"{trigger} This skill is specific to {env['name']}."
    skill_md = f'''---
name: {skill_name}
description: {yaml_quote(description)}
---

# {display_name}: {env["name"]}

{procedure}

## Environment

```json
{json.dumps(env, indent=2, sort_keys=True)}
```

## Capabilities

{sections}

## Policies

```json
{policies}
```

## Conventions

```json
{conventions}
```

## Operating rules

- Treat command strings as templates. Inspect substitutions and applicable approval gates before execution.
- Keep credentials out of prompts, logs, artifacts, and generated files. Resolve only the recorded secret references at execution time.
- State when a required capability is unavailable and stop before fabricating infrastructure.
- Prefer immutable identifiers for datasets, runs, artifacts, models, and releases.
- Default tabular working snapshots to Apache Parquet. Preserve upstream raw files and record the conversion plus fingerprints for both raw and derived data.
- Begin with read-only checks. Do not infer permission for production mutations from a diagnostic or build request.
'''
    openai_yaml = f'''interface:
  display_name: {yaml_quote(display_name + " — " + env["name"])}
  short_description: {yaml_quote((trigger.split(".")[0])[:64])}
  default_prompt: {yaml_quote(f"Use ${skill_name} to help with this model lifecycle task.")}
'''
    return skill_md, openai_yaml


def generate(data: dict[str, Any], output: Path) -> Path:
    env = data["environment"]
    slug = slugify(str(env.get("slug") or env["name"]))
    destination = output / f"{slug}-ml-skillpack"
    if destination.exists():
        raise ValueError(f"destination already exists: {destination}")
    (destination / "skills").mkdir(parents=True)
    normalized = dict(data)
    normalized["environment"] = dict(env, slug=slug)
    (destination / "environment.json").write_text(
        json.dumps(normalized, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    for suffix, (display, trigger, capability_names, procedure) in SKILLS.items():
        skill_name = f"{slug}-{suffix}"
        skill_dir = destination / "skills" / skill_name
        (skill_dir / "agents").mkdir(parents=True)
        skill_md, openai_yaml = make_skill(
            skill_name, display, trigger, capability_names, procedure, normalized
        )
        (skill_dir / "SKILL.md").write_text(skill_md, encoding="utf-8")
        (skill_dir / "agents" / "openai.yaml").write_text(openai_yaml, encoding="utf-8")
    return destination


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    validate_parser = subparsers.add_parser("validate", help="validate a manifest")
    validate_parser.add_argument("manifest", type=Path)
    generate_parser = subparsers.add_parser("generate", help="generate a new skillpack")
    generate_parser.add_argument("manifest", type=Path)
    generate_parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    try:
        data = load_manifest(args.manifest)
        errors = validate(data)
        if errors:
            for error in errors:
                print(f"ERROR: {error}", file=sys.stderr)
            return 2
        if args.command == "validate":
            print(f"valid: {args.manifest}")
        else:
            destination = generate(data, args.output)
            print(destination)
        return 0
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
