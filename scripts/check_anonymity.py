#!/usr/bin/env python3
"""Fail when the public repository contains common identity or path leaks."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SKIP_PARTS = {".git", ".venv", ".pytest_cache", "__pycache__", "generated"}
EMAIL_RE = re.compile(
    rb"(?i)(?<![a-z0-9._%+-])[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}"
)
NEUTRAL_EMAILS = {b"anonymous@invalid"}
EMBEDDED_PROVENANCE_MARKERS = (
    b"gpt" + b"-image",
    b"software" + b"age" + b"nt",
    b"trained" + b"algorithmicmedia",
    b"open" + b"ai media service",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--forbidden-term",
        action="append",
        default=[],
        help="Additional case-insensitive literal to reject; repeat as needed.",
    )
    parser.add_argument(
        "--allow-remote",
        action="store_true",
        help="Do not reject configured Git remotes (use only after the clean-tree audit).",
    )
    return parser.parse_args()


def tracked_or_candidate_files() -> list[Path]:
    return sorted(
        path
        for path in REPO_ROOT.rglob("*")
        if path.is_file() and not any(part in SKIP_PARTS for part in path.relative_to(REPO_ROOT).parts)
    )


def git_output(*args: str) -> str:
    process = subprocess.run(
        ["git", "-C", str(REPO_ROOT), *args],
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        text=True,
    )
    return process.stdout.strip() if process.returncode == 0 else ""


def scan_payload(path: Path) -> bytes:
    """Inspect decoded Parquet strings and metadata, not compressed numeric bytes."""
    if path.suffix != ".parquet":
        return path.read_bytes()
    import pyarrow as pa
    import pyarrow.parquet as pq

    table = pq.read_table(path)
    blocks = [str(table.schema).encode("utf-8")]
    for key, value in (table.schema.metadata or {}).items():
        blocks.extend([key, value])
    for field, column in zip(table.schema, table.columns):
        # Nested and dictionary columns may also contain strings or binary text.
        if not (pa.types.is_integer(field.type) or pa.types.is_floating(field.type)
                or pa.types.is_boolean(field.type) or pa.types.is_temporal(field.type)):
            blocks.append(json.dumps(column.to_pylist(), ensure_ascii=False, default=str).encode("utf-8"))
    return b"\n".join(blocks)


def main() -> None:
    args = parse_args()
    findings: list[str] = []
    home_prefix = ("/" + "home" + "/").encode()
    users_prefix = ("/" + "Users" + "/").encode()
    extra_terms = [term.casefold().encode("utf-8") for term in args.forbidden_term if term]

    for path in tracked_or_candidate_files():
        relative = path.relative_to(REPO_ROOT)
        try:
            payload = scan_payload(path)
        except (OSError, ValueError) as exc:
            findings.append(f"{relative}: cannot read ({exc})")
            continue
        lowered = payload.lower()
        if home_prefix.lower() in lowered:
            findings.append(f"{relative}: Unix home-directory path")
        if users_prefix.lower() in lowered:
            findings.append(f"{relative}: macOS user-directory path")
        for email in EMAIL_RE.findall(payload):
            if email.lower() not in NEUTRAL_EMAILS:
                findings.append(f"{relative}: email address")
        for marker in EMBEDDED_PROVENANCE_MARKERS:
            if marker in lowered:
                findings.append(f"{relative}: embedded image-generation provenance")
        for term in extra_terms:
            if term in lowered:
                findings.append(f"{relative}: additional forbidden term")

    for path in REPO_ROOT.rglob("*"):
        if path.is_symlink():
            findings.append(f"{path.relative_to(REPO_ROOT)}: symbolic link")

    if not args.allow_remote and git_output("remote"):
        findings.append("Git metadata: configured remote")
    authors = git_output("log", "--format=%an <%ae>")
    if authors:
        unexpected = sorted(
            {line for line in authors.splitlines() if line != "Anonymous Authors <anonymous@invalid>"}
        )
        if unexpected:
            findings.append("Git metadata: non-anonymous commit identity")

    if findings:
        print("Anonymity audit failed:")
        for finding in sorted(set(findings)):
            print(f"  - {finding}")
        raise SystemExit(1)
    print(f"Anonymity audit passed ({len(tracked_or_candidate_files())} files checked).")


if __name__ == "__main__":
    main()
