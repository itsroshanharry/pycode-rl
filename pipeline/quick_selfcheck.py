"""Fast author-side sanity check: run each task's tests directly against its own
reference.py (no grader, no isolation). This executes only task-author code, never
model output, so it is safe on the laptop. It catches wrong expected values early;
the real gates are 02a/02b (grader, Codespace) and vf-validate (Prime sandboxes).
Usage: uv run python pipeline/quick_selfcheck.py tasks/generated/b04_claude [task_dir ...]
"""

from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


def check(task_dir: Path) -> bool:
    with tempfile.TemporaryDirectory() as d:
        shutil.copy(task_dir / "reference.py", Path(d, "solution.py"))
        shutil.copy(task_dir / "tests.py", Path(d, "test_task.py"))
        p = subprocess.run([sys.executable, "-m", "pytest", "-q", "-x", "-p", "no:cacheprovider", "test_task.py"],
                           cwd=d, capture_output=True, text=True, timeout=600)
    ok = p.returncode == 0
    summary = p.stdout.strip().splitlines()[-1] if p.stdout.strip() else p.stderr[-300:]
    print(f"{'OK  ' if ok else 'FAIL'} {task_dir.name}: {summary}")
    if not ok:
        print("\n".join(line for line in p.stdout.splitlines() if line.startswith(("E ", "FAILED", ">")))[:2000])
    return ok


def main() -> None:
    dirs = []
    for arg in sys.argv[1:]:
        p = Path(arg)
        dirs += sorted(x for x in p.iterdir() if x.is_dir()) if not (p / "reference.py").exists() else [p]
    results = [check(d) for d in dirs if (d / "reference.py").exists()]
    print(f"{sum(results)}/{len(results)} pass")


if __name__ == "__main__":
    main()
