"""Stage 5: train/test split + export (data only; safe on Windows).

  uv run python pipeline/05_split_export.py
      reads  data/decontaminated.jsonl
      writes data/dataset.jsonl and environments/pycode/pycode_env/data/dataset.jsonl
             (identical files, seeded order) + data/reports/split.json (sha256, counts)

Rules (decided 2026-11-20):
- About 50/50 train/test. This project only evaluates, and the leaderboard needs enough test
  tasks for usable confidence intervals; the train half keeps the dataset usable for RL.
- SEEN tasks go to train: tasks whose leaderboard-model results were inspected during the
  pilots / v3 check, or whose spec was changed after seeing model results. The test split
  then holds only tasks nobody tuned anything on.
- Unseen tasks are split stratified by difficulty band (filter pass-rate bucket or triage
  tier) and prompt version, with a fixed seed, so both halves get a similar mix.
"""
import collections
import json
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "pipeline"))
from taskfiles import write_rows  # noqa: E402

SEED = 2026
PILOT_REPORTS = ["pilot-20x4-8k.json", "v3check-deepseek.json"]  # per_task keys = inspected tasks
CHANGED_AFTER_RESULTS = ["pc-c-0004", "pc-c-0036"]  # c0004 spec fixed after triage; c0036 kept by manual decision
OUT = [ROOT / "data" / "dataset.jsonl", ROOT / "environments" / "pycode" / "pycode_env" / "data" / "dataset.jsonl"]


def _band(meta: dict) -> str:
    b = meta.get("difficulty_band")
    if b != "filter":
        return "hard"  # hard_triage / hard_manual
    p = meta["pass_rate"]
    return "low" if p <= 2 / 8 else "mid" if p <= 5 / 8 else "high"


def _version(row: dict) -> str:
    return row.get("meta", {}).get("prompt_version") or ("handwritten" if row["id"].startswith("pc-hw") else "v1")


def main() -> None:
    rows = [json.loads(l) for l in (ROOT / "data" / "decontaminated.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
    seen = set(CHANGED_AFTER_RESULTS)
    for name in PILOT_REPORTS:
        seen |= set(json.loads((ROOT / "data" / "reports" / "pilot" / name).read_text())["per_task"])
    ids = {r["id"] for r in rows}
    seen &= ids
    n_test = len(rows) // 2
    unseen = sorted((r for r in rows if r["id"] not in seen), key=lambda r: r["id"])
    if n_test > len(unseen):
        raise SystemExit(f"only {len(unseen)} unseen tasks for {n_test} test slots")

    # Proportional allocation of test slots over strata of the unseen pool (largest remainder).
    strata = collections.defaultdict(list)
    for r in unseen:
        strata[(_band(r["meta"]), _version(r))].append(r)
    quota = {k: n_test * len(v) / len(unseen) for k, v in strata.items()}
    alloc = {k: int(q) for k, q in quota.items()}
    for k in sorted(quota, key=lambda k: (quota[k] - alloc[k], k), reverse=True)[: n_test - sum(alloc.values())]:
        alloc[k] += 1
    rng = random.Random(SEED)
    test_ids = set()
    for k in sorted(strata):
        group = strata[k][:]
        rng.shuffle(group)
        test_ids |= {r["id"] for r in group[: alloc[k]]}

    out_rows = []
    for r in rows:
        split = "test" if r["id"] in test_ids else "train"
        out_rows.append({**r, "split": split, "meta": {**r["meta"], "version": "v1"}})
    sha = write_rows(out_rows, OUT, seed=SEED)
    count = collections.Counter((r["split"], _band(r["meta"])) for r in out_rows)
    report = {
        "sha256": sha, "seed": SEED, "total": len(out_rows),
        "train": sum(r["split"] == "train" for r in out_rows), "test": sum(r["split"] == "test" for r in out_rows),
        "seen_forced_to_train": sorted(seen),
        "by_split_and_band": {f"{s}/{b}": n for (s, b), n in sorted(count.items())},
        "by_split_and_version": {f"{s}/{v}": n for (s, v), n in sorted(collections.Counter((r["split"], _version(r)) for r in out_rows).items())},
        "test_ids": sorted(test_ids),
    }
    (ROOT / "data" / "reports" / "split.json").write_text(json.dumps(report, indent=1) + "\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in report.items() if k not in ("test_ids", "seen_forced_to_train")}, indent=1))
    print(f"{len(seen)} seen tasks forced to train")


if __name__ == "__main__":
    main()
