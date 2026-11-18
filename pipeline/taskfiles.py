"""Shared task-folder logic: turn a task directory into a dataset row.

A task directory holds meta.json, prompt.md, reference.py, tests.py and mutants.py
(a Python list literal of (description, find, replace) patches over reference.py).
Used by 00_build_handwritten.py and 01_assemble_candidates.py.
"""

from __future__ import annotations

import ast
import hashlib
import json
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class TaskFormatError(Exception):
    pass


def build_row(task_dir: Path, split: str, extra_meta: dict | None = None) -> dict:
    meta = json.loads((task_dir / "meta.json").read_text(encoding="utf-8"))
    reference = (task_dir / "reference.py").read_text(encoding="utf-8")
    patches = ast.literal_eval((task_dir / "mutants.py").read_text(encoding="utf-8"))
    mutants, descriptions = [], []
    for desc, find, replace in patches:
        hits = reference.count(find)
        if hits != 1:
            raise TaskFormatError(f"{task_dir.name}: mutant {desc!r} patch matches {hits} times (need exactly 1)")
        mutant = reference.replace(find, replace)
        if mutant == reference:
            raise TaskFormatError(f"{task_dir.name}: mutant {desc!r} is identical to the reference")
        try:
            compile(mutant, f"{task_dir.name}/mutant", "exec")
        except SyntaxError as e:
            raise TaskFormatError(f"{task_dir.name}: mutant {desc!r} is not valid Python: {e}") from None
        mutants.append(mutant)
        descriptions.append(desc)
    tests = (task_dir / "tests.py").read_text(encoding="utf-8")
    if f"from solution import {meta['entry_point']}" not in tests:
        raise TaskFormatError(f"{task_dir.name}: tests must import {meta['entry_point']} from solution")
    compile(reference, f"{task_dir.name}/reference.py", "exec")
    compile(tests, f"{task_dir.name}/tests.py", "exec")
    row_meta = {k: v for k, v in meta.items() if k not in ("id", "entry_point")}
    row_meta.update(mutant_descriptions=descriptions, source_dir=task_dir.relative_to(ROOT).as_posix(), version="v1")
    row_meta.update(extra_meta or {})
    return {
        "id": meta["id"],
        "split": split,
        "prompt": (task_dir / "prompt.md").read_text(encoding="utf-8").strip(),
        "entry_point": meta["entry_point"],
        "tests": tests,
        "reference": reference,
        "mutants": mutants,
        "meta": row_meta,
    }


def write_rows(rows: list[dict], paths: list[Path], seed: int = 0) -> str:
    """Write rows in a seeded shuffled order to every path; return the sha256."""
    ids = [r["id"] for r in rows]
    if len(set(ids)) != len(ids):
        raise TaskFormatError("duplicate task ids")
    rows = sorted(rows, key=lambda r: r["id"])
    random.Random(seed).shuffle(rows)
    text = "".join(json.dumps(r, ensure_ascii=False, sort_keys=True) + "\n" for r in rows)
    for path in paths:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8", newline="\n")
    return hashlib.sha256(text.encode("utf-8")).hexdigest()
