"""Free pre-check of candidates with the real grader, before paid `vf-validate` runs.

For every row in data/candidates.jsonl it runs grader/run_pytest.py on the reference
and on each mutant, then records the outcome in data/reports/local_check.json:
- does the reference pass;
- how many tests there are;
- which mutants survive;
- the first failure.
A candidate is locally OK if the reference scores 1.0 and at least 2 of its 3 mutants
score 0.0, the same gate as Task.validate.

Linux only (the grader uses rlimits/setuid). Run it in the Codespace as root so the
worker drops privileges exactly as in a Prime sandbox:
  sudo .venv/bin/python pipeline/02a_local_check.py
It executes task-author code (references and mutants), never model output.
"""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GRADER = ROOT / "environments" / "pycode" / "pycode_env" / "grader" / "run_pytest.py"
CANDIDATES = ROOT / "data" / "candidates.jsonl"
REPORT = ROOT / "data" / "reports" / "local_check.json"
MIN_KILLED = 2


def grade(code: str, tests: str) -> dict:
    with tempfile.TemporaryDirectory() as d:
        sol, tst = Path(d, "solution.py"), Path(d, "tests.py")
        sol.write_text(code)
        tst.write_text(tests)
        p = subprocess.run([sys.executable, str(GRADER), str(sol), str(tst)], capture_output=True, text=True, timeout=600)
    if p.returncode != 0:
        return {"grader_error": p.stderr[-1500:]}
    return json.loads(p.stdout.strip().splitlines()[-1])


def check(row: dict) -> dict:
    started = time.monotonic()
    ref = grade(row["reference"], row["tests"])
    ref_seconds = round(time.monotonic() - started, 2)  # includes grader start-up (~1 s)
    out = {"id": row["id"], "seed_id": row["meta"].get("seed_id"), "difficulty": row["meta"].get("difficulty_hint")}
    if "grader_error" in ref:
        return {**out, "ok": False, "reason": "tests broken (grader error)", "detail": ref["grader_error"]}
    out.update(tests=ref["total"], reference_score=ref["score"], isolated=ref["isolated"], reference_seconds=ref_seconds)
    if ref["score"] != 1.0:
        return {**out, "ok": False, "reason": "reference fails its own tests", "detail": ref["first_failure"]}
    if "slow_reference" in row:
        slow = grade(row["slow_reference"], row["tests"])
        out["slow_timeouts"] = slow.get("timeouts")
        # The naive solution must lose specifically by timing out, not by being wrong.
        if slow.get("score") != 0.0 or not slow.get("timeouts"):
            return {**out, "ok": False, "reason": "efficiency test does not reject the naive slow.py", "detail": slow.get("first_failure")}
    survived = []
    for desc, mutant in zip(row["meta"]["mutant_descriptions"], row["mutants"]):
        g = grade(mutant, row["tests"])
        if g.get("score") != 0.0:
            survived.append(desc)
    killed = len(row["mutants"]) - len(survived)
    ok = killed >= MIN_KILLED
    return {**out, "ok": ok, "mutants_killed": f"{killed}/{len(row['mutants'])}", "survived": survived,
            "reason": None if ok else "tests too weak (mutants survive)"}


def main() -> None:
    rows = [json.loads(line) for line in CANDIDATES.read_text().splitlines() if line.strip()]
    with ThreadPoolExecutor(max_workers=4) as pool:
        results = sorted(pool.map(check, rows), key=lambda r: r["id"])
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(results, indent=2) + "\n")
    for r in results:
        status = "OK  " if r["ok"] else "FAIL"
        extra = r.get("mutants_killed") or ""
        print(f"{status} {r['id']:<12} tests={r.get('tests', '-'):<4} mutants={extra:<4} {r['reason'] or ''} {r.get('survived') or ''}")
        if not r["ok"] and r.get("detail"):
            print("      ", str(r["detail"]).replace("\n", " ")[:300])
    print(f"{sum(r['ok'] for r in results)}/{len(results)} candidates pass the local check")


if __name__ == "__main__":
    main()
