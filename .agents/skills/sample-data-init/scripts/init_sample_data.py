#!/usr/bin/env python3
"""Download, normalize, fingerprint, and validate the sample tabular datasets."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import pyarrow.parquet as pq
from pandas.api.types import is_object_dtype, is_string_dtype


ATTRIBUTE = re.compile(
    r"^@attribute\s+(?:'([^']+)'|\"([^\"]+)\"|(\S+))\s+", re.IGNORECASE
)
BUFFER_SIZE = 1024 * 1024


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(BUFFER_SIZE), b""):
            digest.update(block)
    return digest.hexdigest()


def require_ignored(repo_root: Path, data_dir: Path) -> None:
    try:
        relative = data_dir.relative_to(repo_root)
    except ValueError as exc:
        raise RuntimeError("data directory must be inside the repository root") from exc
    probe = relative / ".sample-data-ignore-check"
    result = subprocess.run(
        ["git", "check-ignore", "--quiet", str(probe)],
        cwd=repo_root,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(f"{data_dir} is not ignored by Git")


def download(url: str, destination: Path, expected_sha256: str) -> None:
    if destination.exists():
        actual = sha256(destination)
        if actual != expected_sha256:
            raise RuntimeError(
                f"checksum mismatch for existing {destination}: {actual}"
            )
        print(f"raw OK: {destination}")
        return

    destination.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        dir=destination.parent, prefix=destination.name + ".", suffix=".part", delete=False
    ) as temporary:
        temporary_path = Path(temporary.name)
        try:
            request = urllib.request.Request(url, headers={"User-Agent": "sample-data-init/1"})
            with urllib.request.urlopen(request) as response:
                shutil.copyfileobj(response, temporary, length=BUFFER_SIZE)
        except Exception:
            temporary_path.unlink(missing_ok=True)
            raise

    actual = sha256(temporary_path)
    if actual != expected_sha256:
        temporary_path.unlink(missing_ok=True)
        raise RuntimeError(
            f"download checksum mismatch for {url}: expected {expected_sha256}, got {actual}"
        )
    os.replace(temporary_path, destination)
    print(f"downloaded: {destination}")


def read_arff(path: Path) -> pd.DataFrame:
    columns: list[str] = []
    data_start: int | None = None
    with path.open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle):
            stripped = line.strip()
            match = ATTRIBUTE.match(stripped)
            if match:
                columns.append(next(value for value in match.groups() if value is not None))
            if stripped.lower() == "@data":
                data_start = line_number + 1
                break
    if data_start is None:
        raise RuntimeError(f"missing @data marker in {path}")

    frame = pd.read_csv(
        path,
        skiprows=data_start,
        names=columns,
        na_values=["?"],
        skipinitialspace=True,
        low_memory=False,
    )
    for column in frame.columns:
        if is_object_dtype(frame[column].dtype) or is_string_dtype(frame[column].dtype):
            frame[column] = frame[column].str.strip().str.replace(
                r"^(?:'(.*)'|\"(.*)\")$",
                lambda match: match.group(1) or match.group(2),
                regex=True,
            )
    return frame


def materialize_parquet(
    raw: Path,
    destination: Path,
    raw_format: str,
    existing_sha256: str | None,
) -> None:
    if destination.exists():
        if existing_sha256 is None:
            raise RuntimeError(
                f"existing {destination} has no fingerprint in the current catalog"
            )
        actual = sha256(destination)
        if actual != existing_sha256:
            raise RuntimeError(
                f"checksum mismatch for existing {destination}: {actual}"
            )
        print(f"parquet exists: {destination}")
        return
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = destination.with_name(destination.name + ".part")
    temporary.unlink(missing_ok=True)
    try:
        if raw_format == "parquet":
            shutil.copyfile(raw, temporary)
        elif raw_format == "arff":
            read_arff(raw).to_parquet(temporary, index=False, compression="zstd")
        else:
            raise RuntimeError(f"unsupported raw format: {raw_format}")
        os.replace(temporary, destination)
    except Exception:
        temporary.unlink(missing_ok=True)
        raise
    print(f"materialized: {destination}")


def validate_parquet(path: Path, rows: int, columns: int) -> None:
    metadata = pq.ParquetFile(path).metadata
    actual = (metadata.num_rows, metadata.num_columns)
    expected = (rows, columns)
    if actual != expected:
        raise RuntimeError(f"shape mismatch for {path}: expected {expected}, got {actual}")
    print(f"shape OK: {path} ({rows} x {columns})")


def load_manifest() -> dict:
    path = Path(__file__).resolve().parent.parent / "references" / "datasets.json"
    manifest = json.loads(path.read_text(encoding="utf-8"))
    for dataset in manifest.get("datasets", []):
        description = dataset.get("description")
        if not isinstance(description, str) or not description.strip():
            raise RuntimeError(
                f"dataset {dataset.get('slug', '<unknown>')} needs a description"
            )
        if "\n" in description or description[-1] not in ".!?":
            raise RuntimeError(
                f"dataset {dataset.get('slug', '<unknown>')} description must be one sentence"
            )
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument("--data-dir", type=Path)
    args = parser.parse_args()

    repo_root = args.repo_root.resolve()
    data_dir = (args.data_dir or repo_root / "data").resolve()
    require_ignored(repo_root, data_dir)
    manifest = load_manifest()
    catalog_path = data_dir / "catalog.json"
    existing_fingerprints: dict[str, str] = {}
    if catalog_path.exists():
        existing_catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
        existing_fingerprints = {
            item["default_path"]: item["parquet_sha256"]
            for item in existing_catalog.get("datasets", [])
            if item.get("default_path") and item.get("parquet_sha256")
        }
    catalog = {
        "schema_version": 2,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "default_format": "parquet",
        "datasets": [],
    }

    for dataset in manifest["datasets"]:
        raw = data_dir / dataset["raw_path"]
        parquet = data_dir / dataset["parquet_path"]
        download(dataset["url"], raw, dataset["raw_sha256"])
        materialize_parquet(
            raw,
            parquet,
            dataset["raw_format"],
            existing_fingerprints.get(dataset["parquet_path"]),
        )
        validate_parquet(parquet, dataset["rows"], dataset["columns"])
        record = dict(dataset)
        record.update(
            {
                "default_path": dataset["parquet_path"],
                "raw_bytes": raw.stat().st_size,
                "parquet_bytes": parquet.stat().st_size,
                "parquet_sha256": sha256(parquet),
            }
        )
        catalog["datasets"].append(record)

    catalog_path.write_text(json.dumps(catalog, indent=2) + "\n", encoding="utf-8")
    print(f"catalog: {catalog_path}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)
