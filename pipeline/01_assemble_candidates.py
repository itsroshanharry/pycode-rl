"""Assemble generated candidate tasks (tasks/generated/<batch>/<task>/) into
data/candidates.jsonl.

Each candidate folder uses the task-folder format (pipeline/taskfiles.py) and its
meta.json records seed_id, generator and prompt_version. A folder that fails the
format checks (patch doesn't apply exactly once, invalid Python, missing import) is
reported and skipped, and counts as a rejection in the funnel. It is never silently
fixed.
Run: uv run python pipeline/01_assemble_candidates.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from taskfiles import ROOT, TaskFormatError, build_row, write_rows  # noqa: E402

GENERATED = ROOT / "tasks" / "generated"
OUT = ROOT / "data" / "candidates.jsonl"
REPORT = ROOT / "data" / "reports" / "assemble.json"


def main() -> None:
    rows, rejected = [], []
    for task_dir in sorted(p for p in GENERATED.glob("*/*") if p.is_dir()):
        try:
            # split is assigned later (05_split_export.py); "candidate" until then
            rows.append(build_row(task_dir, split="candidate", extra_meta={"batch": task_dir.parent.name}))
        except (TaskFormatError, SyntaxError, KeyError, ValueError) as e:
            rejected.append({"dir": task_dir.relative_to(ROOT).as_posix(), "reason": str(e)})
    digest = write_rows(rows, [OUT])
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps({"assembled": len(rows), "rejected": rejected, "sha256": digest}, indent=2) + "\n")
    print(f"{len(rows)} candidates -> {OUT.relative_to(ROOT)} (sha256 {digest[:12]}...); {len(rejected)} rejected")
    for r in rejected:
        print(f"  REJECTED {r['dir']}: {r['reason']}")


if __name__ == "__main__":
    main()
