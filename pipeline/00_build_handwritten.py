"""Assemble the hand-written tasks (tasks/handwritten/*) into dataset rows.

Each task directory holds:
  meta.json     {"id", "entry_point", "topic", "difficulty_hint"}
  prompt.md     the spec shown to the model (signature + docstring + examples)
  reference.py  gold solution
  tests.py      hidden pytest file; imports the entry point from `solution`
  mutants.py    a Python list literal of (description, find, replace) patches that
                turn reference.py into a plausible buggy variant

Writes data/handwritten.jsonl and the package copy
environments/pycode/src/pycode_env/data/dataset.jsonl (rows in a seeded shuffled order,
so `-n N` on a hosted eval, which cannot shuffle, takes a representative prefix).
Run: uv run python pipeline/00_build_handwritten.py
"""

from __future__ import annotations

import ast
import hashlib
import json
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TASKS = ROOT / "tasks" / "handwritten"
OUT = ROOT / "data" / "handwritten.jsonl"
PACKAGE_OUT = ROOT / "environments" / "pycode" / "src" / "pycode_env" / "data" / "dataset.jsonl"
SEED = 0


def build_row(task_dir: Path) -> dict:
    meta = json.loads((task_dir / "meta.json").read_text(encoding="utf-8"))
    reference = (task_dir / "reference.py").read_text(encoding="utf-8")
    patches = ast.literal_eval((task_dir / "mutants.py").read_text(encoding="utf-8"))
    mutants, descriptions = [], []
    for desc, find, replace in patches:
        hits = reference.count(find)
        if hits != 1:
            raise SystemExit(f"{task_dir.name}: mutant {desc!r} patch matches {hits} times (need exactly 1)")
        mutant = reference.replace(find, replace)
        if mutant == reference:
            raise SystemExit(f"{task_dir.name}: mutant {desc!r} is identical to the reference")
        mutants.append(mutant)
        descriptions.append(desc)
    tests = (task_dir / "tests.py").read_text(encoding="utf-8")
    if f"from solution import {meta['entry_point']}" not in tests:
        raise SystemExit(f"{task_dir.name}: tests must import {meta['entry_point']} from solution")
    return {
        "id": meta["id"],
        "split": "train",  # hand-written tasks are few-shot exemplars, never held-out test
        "prompt": (task_dir / "prompt.md").read_text(encoding="utf-8").strip(),
        "entry_point": meta["entry_point"],
        "tests": tests,
        "reference": reference,
        "mutants": mutants,
        "meta": {
            "topic": meta["topic"],
            "difficulty_hint": meta["difficulty_hint"],
            "mutant_descriptions": descriptions,
            "generator": "human (hand-written)",
            "source_dir": f"tasks/handwritten/{task_dir.name}",
            "version": "v1",
        },
    }


def main() -> None:
    rows = [build_row(d) for d in sorted(p for p in TASKS.iterdir() if p.is_dir())]
    ids = [r["id"] for r in rows]
    if len(set(ids)) != len(ids):
        raise SystemExit("duplicate task ids")
    random.Random(SEED).shuffle(rows)
    text = "".join(json.dumps(r, ensure_ascii=False, sort_keys=True) + "\n" for r in rows)
    for path in (OUT, PACKAGE_OUT):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8", newline="\n")
    digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
    print(f"{len(rows)} tasks -> {OUT.relative_to(ROOT)} and {PACKAGE_OUT.relative_to(ROOT)}")
    print(f"sha256 {digest}")


if __name__ == "__main__":
    main()
