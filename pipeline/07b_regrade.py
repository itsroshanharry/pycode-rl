"""Re-grade stored leaderboard attempts with the current grader, without new model calls.

Why: grader v2 ran the candidate in a bare namespace, so valid code that looks itself up in
sys.modules (a @dataclass with string annotations, typing.get_type_hints, ...) failed to load.
v3 fixes it. Waves 2-3 ran on v3. Any wave-1 attempt that v2 may have mis-graded is re-graded
here, so that every leaderboard score comes from grader v3.

How: each selected attempt becomes one row whose `reference` is the model's extracted code,
and whose 3 `mutants` are empty programs (these always fail). `vf-validate --only-gold` then
reports the row as valid iff that code passes every hidden test, in a Prime sandbox. So model
code never runs on the laptop, and the grading path is exactly the taskset's own.

  uv run python pipeline/07b_regrade.py build      # -> data/regrade_pending.jsonl (data only)
  # Codespace:
  .venv/bin/vf-validate pycode-env --only-gold --taskset.split all \
      --taskset.dataset_path data/regrade_pending.jsonl -c 2 -o outputs --run.name regrade-v3
  uv run python pipeline/07b_regrade.py record data/reports/leaderboard/regrade-v3.results.jsonl
"""
import argparse
import gzip
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LB = ROOT / "data" / "reports" / "leaderboard"
RAW = ROOT / "outputs" / "leaderboard" / "raw"
DATASET = ROOT / "data" / "dataset.jsonl"
PENDING = ROOT / "data" / "regrade_pending.jsonl"
OUT = LB / "regrade.json"
WAVE1_V2 = {"sejc1ih370l7bvm63dlm8wrh", "d8jyud550zvxewm0bwmvv8ae"}  # eval ids graded by grader v2

SIGNATURE = "'NoneType' object has no attribute '__dict__'"  # dataclasses' lookup of a missing module
FEATURES = re.compile(r"@dataclass|dataclasses|get_type_hints|singledispatch|sys\.modules|__module__|pickle|"
                      r"NamedTuple|TypedDict|inspect\.getmodule")
_FENCE = re.compile(r"```[^\n`]*\n(.*?)```", re.DOTALL)
_THINK = re.compile(r"<think>.*?</think>", re.DOTALL)


def extract_code(reply: str) -> str:
    """Same rule as pycode_env.taskset.extract_code (copied: verifiers does not import on Windows)."""
    text = _THINK.sub("", reply or "")
    blocks = _FENCE.findall(text)
    return (blocks[-1] if blocks else text).strip()


def _reply(doc: dict) -> str:
    for node in reversed(doc.get("nodes") or []):
        msg = node.get("message") or node
        if isinstance(msg, dict) and msg.get("role") == "assistant":
            content = msg.get("content") or ""
            if isinstance(content, list):
                content = " ".join(p.get("text", "") for p in content if isinstance(p, dict))
            return content
    return ""


def cmd_build() -> None:
    tasks = {json.loads(l)["id"]: json.loads(l) for l in DATASET.read_text(encoding="utf-8").splitlines() if l.strip()}
    rows, picked = [], {}
    for f in sorted(LB.glob("rollouts_*.jsonl.gz")):
        with gzip.open(f, "rt", encoding="utf-8") as fh:
            for line in fh:
                r = json.loads(line)
                if r["eval_id"] not in WAVE1_V2 or r["reward"] == 1.0:
                    continue  # a pass cannot be hurt by the bug; v3 runs need no re-grade
                doc = json.loads((RAW / r["eval_id"] / f"{r['trace_id']}.json").read_text(encoding="utf-8"))
                code = extract_code(_reply(doc))
                grade_text = f"{r['grade'].get('load_error') or ''} {r['grade'].get('first_failure') or ''}"
                if SIGNATURE not in grade_text and not FEATURES.search(code):
                    continue
                t = tasks[r["task_id"]]
                rid = f"rg-{r['trace_id'][:12]}"
                rows.append({"id": rid, "split": "all", "prompt": t["prompt"], "entry_point": t["entry_point"],
                             "tests": t["tests"], "reference": code, "mutants": ["", "", ""],
                             "meta": {"regrade_of": r["trace_id"], "task_id": r["task_id"], "model": r["model"]}})
                picked[rid] = {"trace_id": r["trace_id"], "task_id": r["task_id"], "model": r["model"],
                               "v2_reward": r["reward"], "v2_load_error": r["grade"].get("load_error")}
    with PENDING.open("w", encoding="utf-8", newline="\n") as f:
        for row in rows:
            f.write(json.dumps(row) + "\n")
    print(f"{len(rows)} attempt(s) to re-grade -> {PENDING.relative_to(ROOT)}")
    print(json.dumps(picked, indent=1))


def cmd_record(results: str) -> None:
    pending = {json.loads(l)["id"]: json.loads(l)["meta"] for l in PENDING.read_text(encoding="utf-8").splitlines() if l.strip()}
    out = json.loads(OUT.read_text(encoding="utf-8")) if OUT.exists() else {"grader": "3", "attempts": {}}
    for line in Path(results).read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        r = json.loads(line)
        meta = pending[r["name"]]
        gold = r.get("gold") or r
        if gold.get("error"):
            raise RuntimeError(f"{r['name']}: infrastructure error, re-run it: {gold['error']}")
        out["attempts"][meta["regrade_of"]] = {"task_id": meta["task_id"], "model": meta["model"],
                                               "v3_reward": 1.0 if gold["valid"] else 0.0, "v3_reason": gold.get("reason")}
    OUT.write_text(json.dumps(out, indent=1) + "\n", encoding="utf-8")
    print(json.dumps(out, indent=1))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["build", "record"])
    ap.add_argument("results", nargs="?")
    args = ap.parse_args()
    if args.cmd == "build":
        cmd_build()
    else:
        cmd_record(args.results)


if __name__ == "__main__":
    main()
