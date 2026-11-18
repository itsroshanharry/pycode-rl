"""Assemble the hand-written tasks (tasks/handwritten/*) into dataset rows.

Task-folder format: see pipeline/taskfiles.py. Writes data/handwritten.jsonl and the
package copy environments/pycode/pycode_env/data/dataset.jsonl (rows in a seeded
shuffled order, so `-n N` on a hosted eval, which cannot shuffle, takes a
representative prefix).
Run: uv run python pipeline/00_build_handwritten.py
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from taskfiles import ROOT, TaskFormatError, build_row, write_rows  # noqa: E402

TASKS = ROOT / "tasks" / "handwritten"
OUT = ROOT / "data" / "handwritten.jsonl"
PACKAGE_OUT = ROOT / "environments" / "pycode" / "pycode_env" / "data" / "dataset.jsonl"


def main() -> None:
    try:
        rows = [
            # hand-written tasks are few-shot exemplars, never held-out test
            build_row(d, split="train", extra_meta={"generator": "human (hand-written)"})
            for d in sorted(p for p in TASKS.iterdir() if p.is_dir())
        ]
        digest = write_rows(rows, [OUT, PACKAGE_OUT])
    except TaskFormatError as e:
        raise SystemExit(str(e)) from None
    print(f"{len(rows)} tasks -> {OUT.relative_to(ROOT)} and {PACKAGE_OUT.relative_to(ROOT)}")
    print(f"sha256 {digest}")


if __name__ == "__main__":
    main()
