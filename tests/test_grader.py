"""Adversarial tests for the grader (environments/pycode/.../grader/run_pytest.py).

Every file in grader_fixture/cheats/ is a reward-hacking or broken submission and must
score 0 (with the grader itself still exiting 0). Every file in grader_fixture/legit/
must score 1. Runs on Linux only (the grader uses rlimits/setuid). Run it as root
(e.g. `sudo .venv/bin/python -m pytest tests/test_grader.py`) to exercise the privilege
drop; as a normal user the isolation-dependent cases are skipped.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import time
from pathlib import Path

import pytest

pytestmark = pytest.mark.skipif(sys.platform == "win32", reason="the grader needs Linux")

ROOT = Path(__file__).resolve().parents[1]
GRADER = ROOT / "environments" / "pycode" / "pycode_env" / "grader" / "run_pytest.py"
FIXTURE = Path(__file__).parent / "grader_fixture"
TESTS_SRC = (FIXTURE / "tests.py").read_text()
IS_ROOT = sys.platform != "win32" and os.geteuid() == 0
# These cheats can only be stopped by the uid drop (reading root-only files,
# signalling the grader), so they are meaningful only when the grader runs as root.
NEEDS_ISOLATION = {"read_hidden_tests.py", "kill_grader.py"}


def grade(solution_src: str, tmp_path: Path, tests_src: str = TESTS_SRC) -> tuple[subprocess.CompletedProcess, dict | None]:
    sol, tests = tmp_path / "solution.py", tmp_path / "tests.py"
    sol.write_text(solution_src)
    tests.write_text(tests_src)
    proc = subprocess.run(
        [sys.executable, str(GRADER), str(sol), str(tests), "--call-timeout", "2", "--total-timeout", "20"],
        capture_output=True, text=True, timeout=180,
    )
    result = json.loads(proc.stdout.strip().splitlines()[-1]) if proc.returncode == 0 else None
    return proc, result


@pytest.mark.parametrize("name", sorted(p.name for p in (FIXTURE / "cheats").glob("*.py")))
def test_cheat_scores_zero(name, tmp_path):
    if name in NEEDS_ISOLATION and not IS_ROOT:
        pytest.skip("needs root to exercise the privilege drop")
    start = time.monotonic()
    proc, result = grade((FIXTURE / "cheats" / name).read_text(), tmp_path)
    assert proc.returncode == 0, proc.stderr[-2000:]
    assert result["score"] == 0.0, result
    assert result["total"] == 8, result  # the whole suite still ran: no early abort
    assert time.monotonic() - start < 90
    assert not (tmp_path / "solution.py").exists() and not (tmp_path / "tests.py").exists()


@pytest.mark.parametrize("name", sorted(p.name for p in (FIXTURE / "legit").glob("*.py")))
def test_legit_scores_one(name, tmp_path):
    proc, result = grade((FIXTURE / "legit" / name).read_text(), tmp_path)
    assert proc.returncode == 0, proc.stderr[-2000:]
    assert result["score"] == 1.0 and result["passed"] == result["total"] == 8, result
    assert result["isolated"] is IS_ROOT


def test_cheat_output_cannot_reach_grader_stdout(tmp_path):
    proc, result = grade((FIXTURE / "cheats" / "print_fake_result.py").read_text(), tmp_path)
    assert proc.stdout.strip().count("\n") == 0  # exactly one line: the grader's own
    assert result["score"] == 0.0


def test_broken_tests_are_a_grader_error_not_a_zero(tmp_path):
    ref = (FIXTURE / "legit" / "reference.py").read_text()
    proc, _ = grade(ref, tmp_path, tests_src="def test_x(:\n    pass\n")
    assert proc.returncode == 2


def test_no_tests_is_a_grader_error(tmp_path):
    ref = (FIXTURE / "legit" / "reference.py").read_text()
    proc, _ = grade(ref, tmp_path, tests_src="from solution import digit_sum\n")
    assert proc.returncode == 2


def test_unicode_decode_error_matches_value_error(tmp_path):
    # UnicodeDecodeError can't be rebuilt from a message alone; the grader must fall back
    # to UnicodeError (still a ValueError) so a correct solution is not failed.
    solution = "def decode(b):\n    return b.decode('utf-8')\n"
    tests = (
        "import pytest\nfrom solution import decode\n\n"
        "def test_ok():\n    assert decode(b'hi') == 'hi'\n\n"
        "def test_bad_utf8_is_a_value_error():\n    with pytest.raises(ValueError):\n        decode(bytes([255]))\n"
    )
    proc, result = grade(solution, tmp_path, tests_src=tests)
    assert proc.returncode == 0, proc.stderr[-2000:]
    assert result["score"] == 1.0, result
