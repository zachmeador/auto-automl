#!/usr/bin/env python3
"""Manage the project's local, uncommitted dataset collection."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    if not slug:
        raise ValueError("dataset name must contain a letter or number")
    return slug


def collection(root: Path) -> Path:
    return root.resolve() / "datasets"


def dataset_dir(root: Path, dataset_id: str) -> Path:
    normalized = slugify(dataset_id)
    if normalized != dataset_id:
        raise ValueError(f"dataset id must be normalized as: {normalized}")
    return collection(root) / normalized


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def source_files(directory: Path) -> list[Path]:
    source = directory / "source"
    if not source.is_dir():
        raise ValueError(f"source directory does not exist: {source}")
    symlinks = sorted(path for path in source.rglob("*") if path.is_symlink())
    if symlinks:
        names = ", ".join(str(path.relative_to(directory)) for path in symlinks)
        raise ValueError(f"source directory must not contain symlinks: {names}")
    partials = sorted(path for path in source.rglob("*.part") if path.is_file())
    if partials:
        names = ", ".join(str(path.relative_to(directory)) for path in partials)
        raise ValueError(f"incomplete download files remain: {names}")
    files = sorted(path for path in source.rglob("*") if path.is_file())
    if not files:
        raise ValueError(f"no files found in {source}")
    return files


def read_manifest(directory: Path) -> dict[str, Any]:
    path = directory / "dataset.json"
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ValueError(f"dataset is not registered: {directory.name}") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"invalid manifest {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise ValueError(f"manifest must contain an object: {path}")
    return value


def prepare(args: argparse.Namespace) -> None:
    dataset_id = slugify(args.dataset_id or args.name)
    directory = dataset_dir(args.root, dataset_id)
    if directory.exists():
        raise ValueError(f"dataset directory already exists: {directory}")
    source = directory / "source"
    source.mkdir(parents=True)
    print(source)


def register(args: argparse.Namespace) -> None:
    directory = dataset_dir(args.root, args.dataset_id)
    manifest_path = directory / "dataset.json"
    if manifest_path.exists():
        raise ValueError(f"dataset is already registered: {args.dataset_id}")
    files = source_files(directory)
    records = []
    for path in files:
        records.append(
            {
                "path": path.relative_to(directory).as_posix(),
                "bytes": path.stat().st_size,
                "sha256": sha256(path),
            }
        )
    manifest = {
        "schema_version": 1,
        "id": args.dataset_id,
        "name": args.name,
        "description": args.description,
        "source": {
            "url": args.source_url,
            "retrieved_at": datetime.now(timezone.utc).isoformat(),
            "license": args.license,
        },
        "files": records,
    }
    temporary = directory / "dataset.json.tmp"
    temporary.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    temporary.replace(manifest_path)
    print(manifest_path)


def list_datasets(args: argparse.Namespace) -> None:
    base = collection(args.root)
    manifests = sorted(base.glob("*/dataset.json")) if base.exists() else []
    if not manifests:
        print("No registered datasets.")
        return
    for path in manifests:
        try:
            manifest = read_manifest(path.parent)
            print(f"{manifest.get('id', path.parent.name)}\t{manifest.get('name', '')}\t{path.parent}")
        except ValueError as exc:
            print(f"INVALID\t{path.parent.name}\t{exc}")


def show(args: argparse.Namespace) -> None:
    manifest = read_manifest(dataset_dir(args.root, args.dataset_id))
    print(json.dumps(manifest, indent=2))


def verify(args: argparse.Namespace) -> None:
    directory = dataset_dir(args.root, args.dataset_id)
    manifest = read_manifest(directory)
    records = manifest.get("files")
    if not isinstance(records, list) or not records:
        raise ValueError("manifest has no file records")
    failures = 0
    for record in records:
        if not isinstance(record, dict) or not isinstance(record.get("path"), str):
            print("INVALID manifest file record", file=sys.stderr)
            failures += 1
            continue
        relative = Path(record["path"])
        source = (directory / "source").resolve()
        path = (directory / relative).resolve()
        if relative.is_absolute() or not path.is_relative_to(source):
            print(f"INVALID PATH {record['path']}")
            failures += 1
            continue
        if not path.is_file():
            print(f"MISSING {record['path']}")
            failures += 1
            continue
        actual = sha256(path)
        if actual != record.get("sha256"):
            print(f"MISMATCH {record['path']}")
            failures += 1
        else:
            print(f"OK {record['path']}")
    if failures:
        raise ValueError(f"verification failed for {failures} file(s)")


def parser() -> argparse.ArgumentParser:
    main = argparse.ArgumentParser(description=__doc__)
    main.add_argument("--root", type=Path, default=Path("data"), help="local data root (default: ./data)")
    commands = main.add_subparsers(dest="command", required=True)

    prepare_parser = commands.add_parser("prepare", help="create an empty source directory")
    prepare_parser.add_argument("name")
    prepare_parser.add_argument("--id", dest="dataset_id")
    prepare_parser.set_defaults(handler=prepare)

    register_parser = commands.add_parser("register", help="register downloaded source files")
    register_parser.add_argument("dataset_id")
    register_parser.add_argument("--name", required=True)
    register_parser.add_argument("--source-url", required=True)
    register_parser.add_argument("--license", required=True)
    register_parser.add_argument("--description", default="")
    register_parser.set_defaults(handler=register)

    list_parser = commands.add_parser("list", help="list registered datasets")
    list_parser.set_defaults(handler=list_datasets)

    show_parser = commands.add_parser("show", help="show a dataset manifest")
    show_parser.add_argument("dataset_id")
    show_parser.set_defaults(handler=show)

    verify_parser = commands.add_parser("verify", help="verify registered file checksums")
    verify_parser.add_argument("dataset_id")
    verify_parser.set_defaults(handler=verify)
    return main


def main() -> int:
    args = parser().parse_args()
    try:
        args.handler(args)
        return 0
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
