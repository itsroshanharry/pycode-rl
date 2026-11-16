"""Local pre-check of the hand-written tasks with the real grader (before paid
`vf-validate` runs in Prime sandboxes): the reference passes every hidden test and at
least 2 of the 3 mutants fail. Linux only; runs the task authors' own code, never
model output.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

pytestmark = pytest.mark.skipif(sys.platform == "win32", reason="the grader needs Linux")

ROOT = Path(__file__).resolve().parents[1]
GRADER = ROOT / "environments" / "pycode" / "src" / "pycode_env" / "grader" / "run_pytest.py"
ROWS = [json.loads(line) for line in (ROOT / "data" / "handwritten.jsonl").read_text().splitlines() if line.strip()]


def grade(solution: str, tests: str, tmp_path: Path, tag: str) -> dict:
    d = tmp_path / tag
    d.mkdir()
    (d / "solution.py").write_text(solution)
    (d / "tests.py").write_text(tests)
    proc = subprocess.run(
        [sys.executable, str(GRADER), str(d / "solution.py"), str(d / "tests.py")],
        capture_output=True, text=True, timeout=300,
    )
    assert proc.returncode == 0, proc.stderr[-3000:]
    return json.loads(proc.stdout.strip().splitlines()[-1])


@pytest.mark.parametrize("row", ROWS, ids=[r["id"] for r in ROWS])
def test_reference_passes_and_mutants_fail(row, tmp_path):
    ref = grade(row["reference"], row["tests"], tmp_path, "reference")
    assert ref["score"] == 1.0, ref
    killed = []
    for i, mutant in enumerate(row["mutants"]):
        g = grade(mutant, row["tests"], tmp_path, f"mutant{i}")
        killed.append(g["score"] == 0.0)
    print(f"{row['id']}: tests={ref['total']} mutants killed={sum(killed)}/{len(killed)} {killed}")
    assert sum(killed) >= 2, list(zip(row["meta"]["mutant_descriptions"], killed))
