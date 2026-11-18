"""Objective test-strength metrics for candidates, independent of the task author.

For every row in data/candidates.jsonl:
1. **Automatic mutation score:** mechanically mutate the reference (AST rewrites:
   comparison and arithmetic operator swaps, and/or swaps, +-1 on integer constants,
   dropped `not`, statements replaced by `pass`). Run the real grader on each mutant
   and report the fraction the hidden tests kill. Some mechanical mutants are
   behaviour-preserving ("equivalent"), so the bar is about 0.8, not 1.0.
2. **Coverage:** line and branch coverage of the reference under the hidden tests,
   via coverage.py (runs the reference directly; it is task-author code, not model output).
3. **Hard-coding check:** a fake solution that only returns the prompt's doctest
   example answers must fail.

Writes data/reports/test_strength.json. Linux only; in the Codespace run as root:
  sudo .venv/bin/python pipeline/02b_test_strength.py [--max-mutants 40]
"""

from __future__ import annotations

import argparse
import ast
import copy
import json
import random
import re
import subprocess
import sys
import tempfile
import zlib
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GRADER = ROOT / "environments" / "pycode" / "pycode_env" / "grader" / "run_pytest.py"
CANDIDATES = ROOT / "data" / "candidates.jsonl"
REPORT = ROOT / "data" / "reports" / "test_strength.json"
MIN_MUTATION_SCORE = 0.80
MIN_BRANCH_COVERAGE = 0.90

_CMP_SWAP = {ast.Lt: ast.LtE, ast.LtE: ast.Lt, ast.Gt: ast.GtE, ast.GtE: ast.Gt, ast.Eq: ast.NotEq, ast.NotEq: ast.Eq}
_BIN_SWAP = {ast.Add: ast.Sub, ast.Sub: ast.Add, ast.Mult: ast.FloorDiv, ast.FloorDiv: ast.Mult, ast.Mod: ast.FloorDiv}


# --------------------------------------------------------------------------- mutants
def _mutation_sites(tree: ast.AST) -> list[tuple[int, str]]:
    """(node index in ast.walk order, kind) for every possible single mutation."""
    sites = []
    for i, node in enumerate(ast.walk(tree)):
        if isinstance(node, ast.Compare) and type(node.ops[0]) in _CMP_SWAP:
            sites.append((i, "cmp"))
        elif isinstance(node, ast.BinOp) and type(node.op) in _BIN_SWAP:
            sites.append((i, "binop"))
        elif isinstance(node, ast.BoolOp):
            sites.append((i, "boolop"))
        elif isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.Not):
            sites.append((i, "not"))
        elif isinstance(node, ast.Constant) and type(node.value) is int and abs(node.value) <= 1000:
            sites += [(i, "const+1"), (i, "const-1")]
        elif isinstance(node, (ast.Assign, ast.AugAssign, ast.Expr, ast.Raise, ast.Return, ast.Continue, ast.Break)) \
                and not (isinstance(node, ast.Expr) and isinstance(node.value, ast.Constant)):
            sites.append((i, "stmt->pass"))
    return sites


class _Apply(ast.NodeTransformer):
    def __init__(self, target: int, kind: str, index: dict[int, int]):
        self.target, self.kind, self.index = target, kind, index

    def generic_visit(self, node):
        node = super().generic_visit(node)
        if self.index.get(id(node)) != self.target:
            return node
        k = self.kind
        if k == "cmp":
            node.ops = [_CMP_SWAP[type(node.ops[0])]()] + node.ops[1:]
        elif k == "binop":
            node.op = _BIN_SWAP[type(node.op)]()
        elif k == "boolop":
            node.op = ast.Or() if isinstance(node.op, ast.And) else ast.And()
        elif k == "not":
            return node.operand
        elif k == "const+1":
            node.value += 1
        elif k == "const-1":
            node.value -= 1
        elif k == "stmt->pass":
            return ast.copy_location(ast.Pass(), node)
        return node


def make_mutants(source: str, max_mutants: int, seed: int) -> list[tuple[str, str]]:
    tree = ast.parse(source)
    sites = _mutation_sites(tree)
    random.Random(seed).shuffle(sites)
    out, seen = [], {ast.unparse(tree)}
    for target, kind in sites:
        mutated = copy.deepcopy(tree)
        index = {id(n): i for i, n in enumerate(ast.walk(mutated))}
        mutated = ast.fix_missing_locations(_Apply(target, kind, index).visit(mutated))
        try:
            code = ast.unparse(mutated)
            compile(code, "mutant", "exec")
        except Exception:
            continue
        if code not in seen:
            seen.add(code)
            out.append((f"{kind}@{target}", code))
        if len(out) >= max_mutants:
            break
    return out


# --------------------------------------------------------------------------- helpers
def grade(code: str, tests: str, call_timeout: float = 2.0, total_timeout: float = 20.0) -> dict:
    with tempfile.TemporaryDirectory() as d:
        sol, tst = Path(d, "solution.py"), Path(d, "tests.py")
        sol.write_text(code)
        tst.write_text(tests)
        p = subprocess.run(
            [sys.executable, str(GRADER), str(sol), str(tst), "--call-timeout", str(call_timeout), "--total-timeout", str(total_timeout)],
            capture_output=True, text=True, timeout=600,
        )
    if p.returncode != 0:
        return {"grader_error": p.stderr[-800:]}
    return json.loads(p.stdout.strip().splitlines()[-1])


def coverage_of(reference: str, tests: str) -> dict:
    with tempfile.TemporaryDirectory() as d:
        Path(d, "solution.py").write_text(reference)
        Path(d, "test_hidden.py").write_text(tests)
        run = [sys.executable, "-m", "coverage", "run", "--branch", "--include=solution.py", "-m", "pytest", "-q", "-p", "no:cacheprovider", "test_hidden.py"]
        subprocess.run(run, cwd=d, capture_output=True, text=True, timeout=600)
        rep = subprocess.run([sys.executable, "-m", "coverage", "json", "-o", "cov.json"], cwd=d, capture_output=True, text=True)
        if rep.returncode != 0:
            return {"error": rep.stderr[-300:]}
        t = json.loads(Path(d, "cov.json").read_text())["totals"]
    lines = t["covered_lines"] / t["num_statements"] if t["num_statements"] else 1.0
    branches = t["covered_branches"] / t["num_branches"] if t["num_branches"] else 1.0
    return {"line": round(lines, 3), "branch": round(branches, 3)}


_DOCTEST = re.compile(r"^\s*>>> (.+)\n\s*(.+)$", re.MULTILINE)


def hardcode_solution(prompt: str, entry_point: str) -> str | None:
    """A fake solution that knows only the prompt's doctest answers."""
    table = {}
    for call, expected in _DOCTEST.findall(prompt):
        captured = {}

        def record(*args, **kwargs):
            captured["key"] = repr((args, kwargs))

        try:
            eval(compile(call.split("  #")[0], "doctest", "eval"), {entry_point: record})  # task-author text
            table[captured["key"]] = ast.literal_eval(expected.strip())
        except Exception:
            continue
    if not table:
        return None
    return f"_T = {table!r}\n\ndef {entry_point}(*args, **kwargs):\n    return _T.get(repr((args, kwargs)))\n"


# --------------------------------------------------------------------------- main
def assess(row: dict, max_mutants: int) -> dict:
    mutants = make_mutants(row["reference"], max_mutants, seed=zlib.crc32(row["id"].encode()))  # stable across processes
    results = [(desc, grade(code, row["tests"])) for desc, code in mutants]
    killed = sum(1 for _, g in results if g.get("score") == 0.0)
    survivors = [desc for desc, g in results if g.get("score") != 0.0]
    fake = hardcode_solution(row["prompt"], row["entry_point"])
    hard = grade(fake, row["tests"]) if fake else None
    cov = coverage_of(row["reference"], row["tests"])
    score = killed / len(results) if results else None
    flags = []
    if score is not None and score < MIN_MUTATION_SCORE:
        flags.append("low mutation score")
    if "branch" in cov and cov["branch"] < MIN_BRANCH_COVERAGE:
        flags.append("low branch coverage")
    if hard is not None and hard.get("score") != 0.0:
        flags.append("hard-coded example answers pass")
    return {
        "id": row["id"], "auto_mutants": len(results), "killed": killed,
        "mutation_score": round(score, 3) if score is not None else None, "survivors": survivors,
        "coverage": cov, "hardcode_fails": None if hard is None else hard.get("score") == 0.0, "flags": flags,
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--max-mutants", type=int, default=40)
    args = ap.parse_args()
    rows = [json.loads(line) for line in CANDIDATES.read_text().splitlines() if line.strip()]
    with ThreadPoolExecutor(max_workers=4) as pool:
        results = sorted(pool.map(lambda r: assess(r, args.max_mutants), rows), key=lambda r: r["id"])
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(results, indent=2) + "\n")
    for r in results:
        cov = r["coverage"]
        print(f"{r['id']:<12} mutation={r['killed']}/{r['auto_mutants']} ({r['mutation_score']})  "
              f"line={cov.get('line')} branch={cov.get('branch')}  hardcode_fails={r['hardcode_fails']}  {r['flags'] or ''}")
    scores = [r["mutation_score"] for r in results if r["mutation_score"] is not None]
    print(f"mean mutation score {sum(scores) / len(scores):.3f}; flagged {sum(bool(r['flags']) for r in results)}/{len(results)}")


if __name__ == "__main__":
    main()
