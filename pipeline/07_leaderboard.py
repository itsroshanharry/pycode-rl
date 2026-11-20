"""Leaderboard: fetch hosted-eval traces and compute per-model statistics. Data only (no model
code is executed here), so it is safe on Windows.

  # 1. per finished hosted run (resumable; raw documents go to the git-ignored outputs/):
  uv run python pipeline/07_leaderboard.py fetch <eval_id> --model <model id>
  # 2. after every run is fetched:
  uv run python pipeline/07_leaderboard.py analyze

`fetch` writes data/reports/leaderboard/rollouts_<model>.jsonl.gz: one compact row per attempt
(reward, tests passed, finish reason, tokens, the model call's cost, the grader's first failure).
`analyze` writes data/reports/leaderboard/summary.json and leaderboard.md.

Statistics, and why:
- pass@1 = mean reward. Two 95% intervals:
  - Wilson over attempts (the usual binomial interval);
  - a task-level bootstrap. This one is the honest one: the 4 attempts on one task are correlated, so
    Wilson over 300 attempts is too narrow.
- pass@k = P(at least one of k attempts passes) and pass^k = P(all k pass), both with unbiased
  estimators from n = 4 attempts. pass^k measures reliability.
- Failure modes come from the grader fields, so a failure can be traced to the model (wrong
  answer, load error, timeout), the harness (truncated by max_tokens) or infrastructure.
- Paired comparison: the same tasks for every model, so the difference is bootstrapped over tasks.
"""
import argparse
import gzip
import json
import math
import os
import random
import re
import shutil
import subprocess
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATASET = ROOT / "data" / "dataset.jsonl"
OUT = ROOT / "data" / "reports" / "leaderboard"
RAW = ROOT / "outputs" / "leaderboard" / "raw"
SEED, BOOT = 2026, 10000
K = 4
SANDBOX_USD_PER_HR = 0.02 + 0.0125 * 1 + 0.0002 * 5  # 1 vCPU, 1 GiB, 5 GiB disk (launch rates, through 2026-12-22)


def _prime(*args: str) -> str:
    env = {**os.environ, "PYTHONUTF8": "1"}
    res = subprocess.run([shutil.which("prime") or "prime", *args], capture_output=True, text=True,
                         encoding="utf-8", env=env, timeout=300)
    if res.returncode:
        raise RuntimeError(f"prime {' '.join(args[:3])} failed: {res.stderr[-500:]}")
    return res.stdout


def _short(model: str) -> str:
    return model.split("/")[-1]


def _rows_file(model: str) -> Path:
    return OUT / f"rollouts_{_short(model)}.jsonl.gz"


_FENCE = re.compile(r"```[^\n`]*\n(.*?)```", re.DOTALL)  # same rule as the taskset's extract_code


def _reply(doc: dict) -> str:
    for node in reversed(doc.get("nodes") or []):
        msg = node.get("message") or node
        if isinstance(msg, dict) and msg.get("role") == "assistant":
            content = msg.get("content") or ""
            if isinstance(content, list):
                content = " ".join(p.get("text", "") for p in content if isinstance(p, dict))
            return content
    return ""


def _sandbox_secs(timing: dict) -> float | None:
    ends = [v["end"] for v in timing.values() if isinstance(v, dict) and v.get("end")]
    start = (timing.get("boot") or {}).get("start") or timing.get("start")
    return round(max(ends) - start, 1) if ends and start else None


def _compact(doc: dict, model: str, eval_id: str, meta: dict) -> dict:
    call = (doc.get("calls") or [{}])[-1]
    usage = call.get("usage") or {}
    grade = (doc.get("info") or {}).get("grade") or {}
    task_id = doc["task"]["data"]["id"]
    m = doc.get("metrics") or {}
    reward = sum(v["score"] * v["weight"] for v in (doc.get("rewards") or {}).values())
    return {
        "model": model, "eval_id": eval_id, "trace_id": doc["id"], "task_id": task_id,
        "split": meta.get(task_id, {}).get("split"), "band": meta.get(task_id, {}).get("band"),
        "prompt_version": meta.get(task_id, {}).get("prompt_version"),
        "reward": reward, "frac_tests_passed": m.get("frac_tests_passed"),
        "no_code": m.get("no_code"), "load_error": m.get("load_error"), "call_timeouts": m.get("call_timeouts"),
        "finish_reason": call.get("finish_reason"), "truncated": call.get("finish_reason") == "length",
        # a reply with no code block (e.g. a refusal) is graded as text, so it shows up as a load error
        "has_code_block": bool(_FENCE.search(_reply(doc))), "reply_chars": len(_reply(doc)),
        "prompt_tokens": usage.get("prompt_tokens"), "completion_tokens": usage.get("completion_tokens"),
        "reasoning_tokens": usage.get("reasoning_tokens"), "cost": usage.get("cost"),
        # wall time of this attempt's own sandbox (boot -> end of grading), for the sandbox-cost estimate
        "sandbox_secs": _sandbox_secs(doc.get("timing") or {}),
        "ok": doc.get("ok"), "is_timeout": doc.get("is_timeout"),
        "errors": [str(e)[:300] for e in (doc.get("errors") or [])],
        "grade": {k: (str(grade[k])[:400] if k in ("first_failure", "load_error") and grade.get(k) else grade.get(k))
                  for k in ("score", "passed", "total", "load_error", "timeouts", "crashes", "isolated", "first_failure")},
    }


def _meta() -> dict:
    out = {}
    for line in DATASET.read_text(encoding="utf-8").splitlines():
        if line.strip():
            r = json.loads(line)
            out[r["id"]] = {"split": r["split"], "band": r["meta"].get("difficulty_band"),
                            "prompt_version": r["meta"].get("prompt_version"),
                            "filter_pass_rate": r["meta"].get("pass_rate")}
    return out


def cmd_fetch(eval_id: str, model: str, workers: int) -> None:
    ids, cursor = [], None
    while True:
        args = ["traces", "list", "--run-id", eval_id, "--limit", "100", "--output", "json"]
        page = json.loads(_prime(*args, *(["--cursor", cursor] if cursor else [])))
        ids += [t["trace_id"] for t in page["items"]]
        cursor = page.get("next_cursor")
        if not cursor:
            break
    raw_dir = RAW / eval_id
    raw_dir.mkdir(parents=True, exist_ok=True)
    print(f"{len(ids)} traces listed for {eval_id}", flush=True)

    def get(tid: str) -> None:
        dest = raw_dir / f"{tid}.json"
        if not dest.exists():  # resumable
            _prime("traces", "get", tid, "--raw", "--dest", str(dest), "--output", "json")

    with ThreadPoolExecutor(max_workers=workers) as pool:
        list(pool.map(get, ids))
    meta = _meta()
    rows = [_compact(json.loads((raw_dir / f"{tid}.json").read_text(encoding="utf-8")), model, eval_id, meta)
            for tid in ids]
    rows.sort(key=lambda r: (r["task_id"], r["trace_id"]))
    OUT.mkdir(parents=True, exist_ok=True)
    with gzip.open(_rows_file(model), "wt", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")
    print(f"wrote {len(rows)} rows -> {_rows_file(model).relative_to(ROOT)}")


# ---------------------------------------------------------------- statistics

def wilson(successes: float, n: int, z: float = 1.96) -> tuple[float, float]:
    if n == 0:
        return (0.0, 0.0)
    p = successes / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (round(c - h, 3), round(c + h, 3))


def bootstrap(values: list[float], rng: random.Random) -> tuple[float, float]:
    """95% percentile interval of the mean, resampling tasks."""
    if not values:
        return (0.0, 0.0)
    n = len(values)
    means = sorted(sum(values[rng.randrange(n)] for _ in range(n)) / n for _ in range(BOOT))
    return (round(means[int(0.025 * BOOT)], 3), round(means[int(0.975 * BOOT) - 1], 3))


def pass_at_k(n: int, c: int, k: int) -> float:
    return 1.0 if n - c < k else 1 - math.comb(n - c, k) / math.comb(n, k)


def pass_hat_k(n: int, c: int, k: int) -> float:
    return math.comb(c, k) / math.comb(n, k) if n >= k else float("nan")


def failure_mode(r: dict) -> str:
    if not r["ok"] or r["errors"]:
        return "infra_error"
    if r["reward"] == 1.0:
        return "pass"
    if r["truncated"]:
        return "truncated"
    if r["no_code"] or r.get("has_code_block") is False:
        return "no_code"  # empty reply, or prose only (e.g. a refusal)
    if r["load_error"]:
        return "load_error"
    if r["call_timeouts"]:
        return "call_timeout"
    return "wrong_answer"


def _model_stats(rows: list[dict], task_ids: list[str], rng: random.Random) -> dict:
    by_task: dict[str, list[dict]] = {t: [] for t in task_ids}
    for r in rows:
        if r["task_id"] in by_task:
            by_task[r["task_id"]].append(r)
    scored = [r for t in task_ids for r in by_task[t] if failure_mode(r) != "infra_error"]
    # a task with no scored attempt (all infra errors / missing) is left out, not counted as 0
    task_means = {t: sum(r["reward"] for r in by_task[t] if failure_mode(r) != "infra_error") /
                  sum(failure_mode(r) != "infra_error" for r in by_task[t])
                  for t in task_ids if any(failure_mode(r) != "infra_error" for r in by_task[t])}
    full = [t for t in task_ids if sum(failure_mode(r) != "infra_error" for r in by_task[t]) >= K]
    pk = {f"pass@{k}": round(sum(pass_at_k(len(by_task[t]), int(sum(r["reward"] == 1.0 for r in by_task[t])), k)
                                 for t in full) / max(1, len(full)), 3) for k in (1, 2, 4)}
    phk = {f"pass^{k}": round(sum(pass_hat_k(len(by_task[t]), int(sum(r["reward"] == 1.0 for r in by_task[t])), k)
                                  for t in full) / max(1, len(full)), 3) for k in (2, 4)}
    modes: dict[str, int] = {}
    for t in task_ids:
        for r in by_task[t]:
            modes[failure_mode(r)] = modes.get(failure_mode(r), 0) + 1
    n_all = sum(len(by_task[t]) for t in task_ids)
    costs = [r["cost"] for t in task_ids for r in by_task[t] if r["cost"] is not None]
    succ = sum(r["reward"] for r in scored)
    hist: dict[int, int] = {}
    for t in full:
        c = int(sum(r["reward"] == 1.0 for r in by_task[t]))
        hist[c] = hist.get(c, 0) + 1
    return {
        "tasks": len(task_ids), "attempts": n_all, "scored_attempts": len(scored),
        "tasks_with_all_attempts": len(full),
        "mean_reward": round(succ / max(1, len(scored)), 3),
        "ci95_wilson_attempts": wilson(succ, len(scored)),
        "tasks_scored": len(task_means),
        "ci95_bootstrap_tasks": bootstrap(list(task_means.values()), rng),
        **pk, **phk,
        "mean_frac_tests_passed": round(sum(r["frac_tests_passed"] or 0 for r in scored) / max(1, len(scored)), 3),
        "truncated_rate": round(sum(r["truncated"] for t in task_ids for r in by_task[t]) / max(1, n_all), 3),
        "infra_error_rate": round(modes.get("infra_error", 0) / max(1, n_all), 3),
        "failure_modes": dict(sorted(modes.items(), key=lambda kv: -kv[1])),
        "pass_count_histogram": dict(sorted(hist.items())),
        "mean_completion_tokens": round(sum(r["completion_tokens"] or 0 for r in scored) / max(1, len(scored))),
        "mean_reasoning_tokens": round(sum(r["reasoning_tokens"] or 0 for r in scored) / max(1, len(scored))),
        "model_cost_usd": round(sum(costs), 4),
        # attempt sandboxes only; the hosted runner sandbox (~$0.29/hr per run) comes from billing rows (runs.json)
        "attempt_sandbox_cost_est_usd": round(sum(r.get("sandbox_secs") or 0 for t in task_ids for r in by_task[t])
                                              / 3600 * SANDBOX_USD_PER_HR, 4),
        "model_cost_per_task_usd": round(sum(costs) / max(1, sum(bool(by_task[t]) for t in task_ids)), 5),
        "_task_means": task_means,
    }


def _paired(a: dict, b: dict, task_ids: list[str], rng: random.Random) -> dict:
    common = [t for t in task_ids if t in a["_task_means"] and t in b["_task_means"]]
    diffs = [a["_task_means"][t] - b["_task_means"][t] for t in common]
    return {"tasks": len(common), "mean_diff": round(sum(diffs) / len(diffs), 3), "ci95_bootstrap_tasks": bootstrap(diffs, rng),
            "a_better_tasks": sum(d > 0 for d in diffs), "b_better_tasks": sum(d < 0 for d in diffs),
            "ties": sum(d == 0 for d in diffs)}


def _pearson(xs: list[float], ys: list[float]) -> float:
    mx, my = sum(xs) / len(xs), sum(ys) / len(ys)
    sx = math.sqrt(sum((x - mx) ** 2 for x in xs))
    sy = math.sqrt(sum((y - my) ** 2 for y in ys))
    return round(sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / (sx * sy), 3) if sx and sy else float("nan")


def cmd_analyze() -> None:
    meta = _meta()
    models = {}
    for f in sorted(OUT.glob("rollouts_*.jsonl.gz")):
        with gzip.open(f, "rt", encoding="utf-8") as fh:
            rows = [json.loads(l) for l in fh if l.strip()]
        models[rows[0]["model"]] = rows
    # attempts re-graded with grader v3 (pipeline/07b_regrade.py) override the hosted v2 reward
    regrade_file = OUT / "regrade.json"
    regraded = json.loads(regrade_file.read_text(encoding="utf-8"))["attempts"] if regrade_file.exists() else {}
    changes = []
    for rows in models.values():
        for r in rows:
            if r["trace_id"] in regraded:
                new = regraded[r["trace_id"]]["v3_reward"]
                if new != r["reward"]:
                    changes.append({"trace_id": r["trace_id"], "task_id": r["task_id"], "from": r["reward"], "to": new})
                r["reward"], r["regraded_v3"] = new, True
    subsets = {
        "all": sorted(meta),
        "test": sorted(t for t in meta if meta[t]["split"] == "test"),
        "train": sorted(t for t in meta if meta[t]["split"] == "train"),
        "band_filter": sorted(t for t in meta if meta[t]["band"] == "filter"),
        "band_hard": sorted(t for t in meta if (meta[t]["band"] or "").startswith("hard")),
    }
    summary: dict = {"dataset_tasks": len(meta), "subsets": {k: len(v) for k, v in subsets.items()},
                     "regraded_v3": {"attempts": len(regraded), "reward_changes": changes}, "by_subset": {}}
    for name, ids in subsets.items():
        rng = random.Random(SEED)
        stats = {m: _model_stats(rows, ids, rng) for m, rows in models.items()}
        order = sorted(stats, key=lambda m: -stats[m]["mean_reward"])
        paired = {f"{a} vs {b}": _paired(stats[a], stats[b], ids, rng)
                  for i, a in enumerate(order) for b in order[i + 1:]}
        summary["by_subset"][name] = {"ranking": order,
                                      "models": {m: {k: v for k, v in s.items() if not k.startswith("_")} for m, s in stats.items()},
                                      "paired": paired}
        if name == "all":
            all_means = {m: s["_task_means"] for m, s in stats.items()}
    filt = "openai/gpt-oss-20b"
    if filt in models:
        ids = [t for t in subsets["all"] if t in all_means[filt]]
        xs = [meta[t]["filter_pass_rate"] for t in ids]
        ys = [all_means[filt][t] for t in ids]
        summary["filter_retest"] = {
            "why": "same model, new attempts: how stable the difficulty estimate is",
            "filter_mean_r8": round(sum(xs) / len(xs), 3), "leaderboard_mean_r4": round(sum(ys) / len(ys), 3),
            "pearson_r": _pearson(xs, ys)}
    summary["per_task"] = {t: {_short(m): (round(all_means[m][t], 2) if t in all_means[m] else None) for m in all_means}
                           for t in subsets["all"]} if models else {}
    (OUT / "summary.json").write_text(json.dumps(summary, indent=1) + "\n", encoding="utf-8")
    (OUT / "leaderboard.md").write_text(_markdown(summary), encoding="utf-8")
    print(_markdown(summary))


def _markdown(s: dict) -> str:
    lines = []
    for name in ("all", "test"):
        sub = s["by_subset"][name]
        lines += [f"### {name} ({s['subsets'][name]} tasks x {K} attempts)", "",
                  "| Model | pass@1 | 95% CI (tasks) | pass@4 | pass^4 | tests passed | truncated | infra err | out tokens | $/task |",
                  "|---|---|---|---|---|---|---|---|---|---|"]
        for m in sub["ranking"]:
            x = sub["models"][m]
            lo, hi = x["ci95_bootstrap_tasks"]
            lines.append(f"| {m} | {x['mean_reward']:.3f} | {lo:.2f}-{hi:.2f} | {x['pass@4']:.3f} | {x['pass^4']:.3f} | "
                         f"{x['mean_frac_tests_passed']:.3f} | {x['truncated_rate']:.1%} | {x['infra_error_rate']:.1%} | "
                         f"{x['mean_completion_tokens']} | {x['model_cost_per_task_usd']:.4f} |")
        lines.append("")
    return "\n".join(lines) + "\n"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["fetch", "analyze"])
    ap.add_argument("eval_id", nargs="?")
    ap.add_argument("--model")
    ap.add_argument("--workers", type=int, default=8)
    args = ap.parse_args()
    if args.cmd == "fetch":
        if not (args.eval_id and args.model):
            ap.error("fetch needs <eval_id> and --model")
        cmd_fetch(args.eval_id, args.model, args.workers)
    else:
        cmd_analyze()


if __name__ == "__main__":
    main()
