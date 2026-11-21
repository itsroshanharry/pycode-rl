"""Stretch: the same tasks and models under the `null` harness (single reply, no tools) and the
`bash` harness (shell + edit tools, multi-turn; `--env.taskset.solution file`, isolated scoring).

  uv run python pipeline/08_harness_compare.py select            # pre-registered task sample
  # Codespace, per model (see NOTES for the exact vf-run command):
  .venv/bin/vf-run pycode-env --env.agent.harness.id bash --env.taskset.solution file ...
  uv run python pipeline/08_harness_compare.py ingest <traces.jsonl[.gz]> --model <id>
  uv run python pipeline/08_harness_compare.py compare

Design:
- Selection: the tasks are chosen from the difficulty-filter results (independent attempts by
  gpt-oss-20b), never from the leaderboard attempts they are compared with. Picking tasks where
  `null` failed would make `bash` look better through regression to the mean alone.
- Baseline: the leaderboard's `null` attempts (4 per task) on the same tasks, same models,
  same sampling. The `bash` attempts come from a separate run.
- Paired comparison per task (bootstrap over tasks), plus the shift in failure modes, turns,
  tokens and cost, and how the solution was delivered (file vs reply fallback).
"""
import argparse
import gzip
import importlib.util
import json
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "reports" / "harness"
LB = ROOT / "data" / "reports" / "leaderboard"
SEED, N_TASKS, MAX_FILTER_PASS = 2026, 20, 0.5

_spec = importlib.util.spec_from_file_location("lb", ROOT / "pipeline" / "07_leaderboard.py")
lb = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(lb)


def cmd_select() -> None:
    meta = lb._meta()
    pool = sorted(t for t, m in meta.items() if (m["filter_pass_rate"] or 0) <= MAX_FILTER_PASS)
    chosen = sorted(random.Random(SEED).sample(pool, N_TASKS))
    OUT.mkdir(parents=True, exist_ok=True)
    sel = {"rule": f"random {N_TASKS} (seed {SEED}) of the tasks whose difficulty-filter pass rate "
                   f"(gpt-oss-20b, 8 attempts) is <= {MAX_FILTER_PASS}; chosen before any bash attempt",
           "pool_size": len(pool), "tasks": chosen,
           "bands": {t: meta[t]["band"] for t in chosen}, "splits": {t: meta[t]["split"] for t in chosen}}
    (OUT / "selection.json").write_text(json.dumps(sel, indent=1) + "\n", encoding="utf-8")
    print(json.dumps(sel, indent=1))


def cmd_ingest(traces: str, model: str) -> None:
    meta = lb._meta()
    opener = gzip.open if traces.endswith(".gz") else open
    rows = []
    with opener(traces, "rt", encoding="utf-8") as fh:
        for line in fh:
            if line.strip():
                rec = json.loads(line)
                for doc in rec.get("traces") or [rec]:
                    row = lb._compact(doc, model, "vf-run:bash", meta)
                    info = doc.get("info") or {}
                    act = [n for n in (doc.get("nodes") or []) if (n.get("message") or n).get("role") == "assistant"]
                    calls = doc.get("calls") or []
                    row.update({
                        "solution_source": info.get("solution_source"),
                        "graded_in_fresh_sandbox": info.get("graded_in_fresh_sandbox"),
                        "model_turns": len(act) or len(calls),
                        "cost": sum(((c.get("usage") or {}).get("cost") or 0) for c in calls),
                        "prompt_tokens": sum(((c.get("usage") or {}).get("prompt_tokens") or 0) for c in calls),
                        "completion_tokens": sum(((c.get("usage") or {}).get("completion_tokens") or 0) for c in calls),
                        "truncated": any(c.get("finish_reason") == "length" for c in calls),
                        "stop_condition": doc.get("stop_condition"),
                    })
                    rows.append(row)
    out = OUT / f"rollouts_{lb._short(model)}_bash.jsonl.gz"
    OUT.mkdir(parents=True, exist_ok=True)
    with gzip.open(out, "wt", encoding="utf-8") as f:
        for r in sorted(rows, key=lambda r: (r["task_id"], r["trace_id"])):
            f.write(json.dumps(r) + "\n")
    print(f"wrote {len(rows)} rows -> {out.relative_to(ROOT)}")


def _load(path: Path) -> list[dict]:
    with gzip.open(path, "rt", encoding="utf-8") as fh:
        return [json.loads(l) for l in fh if l.strip()]


def cmd_compare() -> None:
    import collections
    sel = json.loads((OUT / "selection.json").read_text(encoding="utf-8"))["tasks"]
    result: dict = {"tasks": sel, "models": {}}
    rng = random.Random(SEED)
    for bash_file in sorted(OUT.glob("rollouts_*_bash.jsonl.gz")):
        bash = [r for r in _load(bash_file) if r["task_id"] in sel]
        model = bash[0]["model"]
        null = [r for r in _load(LB / f"rollouts_{lb._short(model)}.jsonl.gz") if r["task_id"] in sel]
        per = {}
        for name, rows in (("null", null), ("bash", bash)):
            by = collections.defaultdict(list)
            for r in rows:
                if lb.failure_mode(r) != "infra_error":
                    by[r["task_id"]].append(r["reward"])
            per[name] = {t: sum(v) / len(v) for t, v in by.items()}
        common = [t for t in sel if t in per["null"] and t in per["bash"]]
        diffs = [per["bash"][t] - per["null"][t] for t in common]
        modes = {name: dict(collections.Counter(lb.failure_mode(r) for r in rows)) for name, rows in (("null", null), ("bash", bash))}
        result["models"][model] = {
            "tasks_compared": len(common),
            "null_pass@1": round(sum(per["null"][t] for t in common) / len(common), 3),
            "bash_pass@1": round(sum(per["bash"][t] for t in common) / len(common), 3),
            "diff_bash_minus_null": round(sum(diffs) / len(diffs), 3),
            "diff_ci95_bootstrap_tasks": lb.bootstrap(diffs, rng),
            "tasks_bash_better": sum(d > 0 for d in diffs), "tasks_null_better": sum(d < 0 for d in diffs),
            "failure_modes": modes,
            "bash_solution_source": dict(collections.Counter(r.get("solution_source") for r in bash)),
            "bash_all_graded_in_fresh_sandbox": all(r.get("graded_in_fresh_sandbox") for r in bash),
            "bash_mean_turns": round(sum(r["model_turns"] for r in bash) / len(bash), 1),
            "mean_prompt_tokens": {"null": round(sum(r["prompt_tokens"] or 0 for r in null) / len(null)),
                                   "bash": round(sum(r["prompt_tokens"] or 0 for r in bash) / len(bash))},
            "mean_completion_tokens": {"null": round(sum(r["completion_tokens"] or 0 for r in null) / len(null)),
                                       "bash": round(sum(r["completion_tokens"] or 0 for r in bash) / len(bash))},
            "model_cost_per_attempt": {"null": round(sum(r["cost"] or 0 for r in null) / len(null), 5),
                                       "bash": round(sum(r["cost"] or 0 for r in bash) / len(bash), 5)},
            "bash_truncated_rate": round(sum(r["truncated"] for r in bash) / len(bash), 3),
        }
    (OUT / "summary.json").write_text(json.dumps(result, indent=1) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=1))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["select", "ingest", "compare"])
    ap.add_argument("traces", nargs="?")
    ap.add_argument("--model")
    args = ap.parse_args()
    if args.cmd == "select":
        cmd_select()
    elif args.cmd == "ingest":
        cmd_ingest(args.traces, args.model)
    else:
        cmd_compare()


if __name__ == "__main__":
    main()
