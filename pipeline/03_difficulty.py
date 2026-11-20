"""Stage 3: difficulty filter (data only; safe on Windows).

The rollouts themselves run in the Codespace with vf-run (verifiers does not import on
Windows). This script prepares the input and summarizes the traces.

  uv run python pipeline/03_difficulty.py prepare
      -> data/filter_input.jsonl (hand-written + all validated candidates)
  # Codespace:
  #   .venv/bin/vf-run pycode-env -m openai/gpt-oss-20b --env.taskset.split all \
  #     --env.taskset.dataset-path data/filter_input.jsonl -r 8 -c 8 --sampling.temperature 1.0 \
  #     --sampling.reasoning-effort low --sampling.max-tokens 8192 -o outputs --run.name difficulty-r8
  uv run python pipeline/03_difficulty.py summarize <traces.jsonl>
      -> data/reports/difficulty.json (histogram, per-task counts, truncation, keep/drop/triage lists)

Rule (CLAUDE.md stage 3): keep pass rate in [1/8, 7/8]. 0/8 tasks get triage (one
attempt with a stronger model; solvable -> keep as "hard", else inspect by hand).
8/8 tasks are dropped as too easy. A task whose failures are mostly truncation is
flagged instead of judged: truncation measures the token cap, not the task.
"""
import argparse
import collections
import gzip
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
INPUT = ROOT / "data" / "filter_input.jsonl"
REPORT = ROOT / "data" / "reports" / "difficulty.json"
SOURCES = [ROOT / "data" / "handwritten.jsonl", ROOT / "data" / "candidates.jsonl"]


def cmd_prepare() -> None:
    rows = []
    for src in SOURCES:
        rows += [json.loads(line) for line in src.read_text(encoding="utf-8").splitlines() if line.strip()]
    ids = [r["id"] for r in rows]
    assert len(ids) == len(set(ids)), "duplicate ids"
    with INPUT.open("w", encoding="utf-8", newline="\n") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"{len(rows)} tasks -> {INPUT.relative_to(ROOT)}")


def cmd_summarize(traces: str, rollouts: int) -> None:
    per = collections.defaultdict(lambda: {"pass": 0, "n": 0, "truncated": 0, "errors": 0})
    for line in Path(traces).read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        r = json.loads(line)
        t = r["traces"][0]
        s = per[t["task"]["data"]["id"]]
        s["n"] += 1
        if not r["ok"] or r["errors"] or t["errors"]:
            s["errors"] += 1  # infra fault: neither a pass nor a model failure
            continue
        call = t["calls"][-1] if t["calls"] else {}
        s["truncated"] += call.get("finish_reason") == "length"
        s["pass"] += sum(v["score"] * v["weight"] for v in t["rewards"].values()) == 1.0
    keep, too_easy, triage, rerun, trunc_flag = [], [], [], [], []
    for tid, s in sorted(per.items()):
        graded = s["n"] - s["errors"]
        if graded < rollouts:
            rerun.append(tid)  # missing or infra-failed rollouts: re-run before judging
            continue
        if s["truncated"] > graded // 2:
            trunc_flag.append(tid)
        if s["pass"] == graded:
            too_easy.append(tid)
        elif s["pass"] == 0:
            triage.append(tid)
        else:
            keep.append(tid)
    hist = collections.Counter(s["pass"] for s in per.values())
    report = {
        "traces": str(traces),
        "rollouts_per_task": rollouts,
        "tasks": len(per),
        "histogram_pass_count": {str(k): hist.get(k, 0) for k in range(rollouts + 1)},
        "keep_1_to_7": keep,
        "drop_too_easy_8_of_8": too_easy,
        "triage_0_of_8": triage,
        "rerun_incomplete": rerun,
        "flag_mostly_truncated": trunc_flag,
        "per_task": {k: v for k, v in sorted(per.items())},
    }
    REPORT.write_text(json.dumps(report, indent=1) + "\n", encoding="utf-8")
    print(json.dumps({k: (len(v) if isinstance(v, list) else v) for k, v in report.items() if k != "per_task"}, indent=1))


def _per_task(paths: list[str]) -> dict[str, dict]:
    """Pass counts per task. A later file REPLACES an earlier one for the tasks it contains
    (used when a task was fixed and re-filtered)."""
    out: dict[str, dict] = {}
    for path in paths:
        seen: dict[str, dict] = {}
        opener = gzip.open if path.endswith(".gz") else open
        with opener(path, "rt", encoding="utf-8") as fh:
            lines = fh.read().splitlines()
        for line in lines:
            if not line.strip():
                continue
            r = json.loads(line)
            t = r["traces"][0]
            s = seen.setdefault(t["task"]["data"]["id"], {"pass": 0, "n": 0, "truncated": 0, "source": path})
            s["n"] += 1
            call = t["calls"][-1] if t["calls"] else {}
            s["truncated"] += call.get("finish_reason") == "length"
            s["pass"] += sum(v["score"] * v["weight"] for v in t["rewards"].values()) == 1.0
        out.update(seen)
    return out


def cmd_finalize(filter_traces: list[str], triage_traces: list[str], manual_keep: list[str], model: str, triage_model: str) -> None:
    filt = _per_task(filter_traces)
    solved_by_triage = {tid for tid, s in _per_task(triage_traces).items() if s["pass"] > 0}
    rows = [json.loads(line) for line in INPUT.read_text(encoding="utf-8").splitlines() if line.strip()]
    kept, decisions = [], {}
    for r in rows:
        s = filt[r["id"]]
        if s["pass"] == s["n"]:
            band = "drop_too_easy"
        elif s["pass"] > 0:
            band = "filter"
        elif r["id"] in solved_by_triage:
            band = "hard_triage"  # filter model 0/n, stronger model solved it
        elif r["id"] in manual_keep:
            band = "hard_manual"  # inspected by hand: spec is clear, kept and flagged for the audit
        else:
            band = "drop_unsolved"
        decisions[r["id"]] = {"band": band, "pass": s["pass"], "n": s["n"]}
        if not band.startswith("drop"):
            meta = dict(r.get("meta", {}))
            meta.update({"pass_rate": round(s["pass"] / s["n"], 4), "filter_model": model,
                         "difficulty_band": band, **({"triage_model": triage_model} if band == "hard_triage" else {})})
            kept.append({**r, "meta": meta})
    out = ROOT / "data" / "filtered.jsonl"
    with out.open("w", encoding="utf-8", newline="\n") as f:
        for r in kept:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    counts = collections.Counter(d["band"] for d in decisions.values())
    summary = {"filter_model": model, "triage_model": triage_model, "filter_traces": filter_traces,
               "triage_traces": triage_traces, "manual_keep": manual_keep, "counts": dict(counts),
               "kept": len(kept), "decisions": decisions}
    (ROOT / "data" / "reports" / "difficulty_final.json").write_text(json.dumps(summary, indent=1) + "\n", encoding="utf-8")
    print(json.dumps({"counts": dict(counts), "kept": len(kept)}, indent=1), f"-> {out.relative_to(ROOT)}")


def main() -> None:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("prepare")
    s = sub.add_parser("summarize")
    s.add_argument("traces")
    s.add_argument("--rollouts", type=int, default=8)
    f = sub.add_parser("finalize", help="combine filter + triage traces -> data/filtered.jsonl")
    f.add_argument("--filter", nargs="+", required=True, help="filter-model traces; later files override earlier ones per task")
    f.add_argument("--triage", nargs="*", default=[], help="stronger-model traces for the 0/n tasks")
    f.add_argument("--manual-keep", nargs="*", default=[], help="0/n task ids kept after manual inspection")
    f.add_argument("--model", default="openai/gpt-oss-20b")
    f.add_argument("--triage-model", default="deepseek/deepseek-v4.1-flash-1017")
    args = ap.parse_args()
    if args.cmd == "prepare":
        cmd_prepare()
    elif args.cmd == "summarize":
        cmd_summarize(args.traces, args.rollouts)
    else:
        cmd_finalize(args.filter, args.triage, args.manual_keep, args.model, args.triage_model)


if __name__ == "__main__":
    main()
