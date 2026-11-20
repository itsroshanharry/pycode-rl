"""Validate only new or changed candidates with vf-validate (paid sandboxes).

Why: re-validating every candidate after each batch repeats work that is already
done, and the run time grows with every batch. A candidate is re-validated only if
its row content changed since it last passed (for example, tests edited after an
auto-mutant finding).

Usage (data only, safe on Windows):
  uv run python pipeline/02c_pending.py write
      -> data/candidates_pending.jsonl (rows whose content hash is not yet validated)
  uv run python pipeline/02c_pending.py record <results.jsonl> [<results.jsonl> ...]
      -> data/reports/validated_hashes.json gains every row of the pending file
         (or of --dataset) that the results mark valid
Then in the Codespace:
  .venv/bin/vf-validate pycode-env --taskset.split all --taskset.dataset_path data/candidates_pending.jsonl -c 5 -o outputs --run.name <name>
A full vf-validate on the frozen final dataset is still run once before publishing.
"""
import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CANDIDATES = ROOT / "data" / "candidates.jsonl"
PENDING = ROOT / "data" / "candidates_pending.jsonl"
HASHES = ROOT / "data" / "reports" / "validated_hashes.json"


def row_hash(row: dict) -> str:
    return hashlib.sha256(json.dumps(row, sort_keys=True, ensure_ascii=False).encode("utf-8")).hexdigest()


def load_rows(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def load_hashes() -> dict[str, str]:
    return json.loads(HASHES.read_text(encoding="utf-8")) if HASHES.exists() else {}


def cmd_write() -> None:
    done = load_hashes()
    rows = load_rows(CANDIDATES)
    pending = [r for r in rows if done.get(r["id"]) != row_hash(r)]
    with PENDING.open("w", encoding="utf-8", newline="\n") as f:
        for r in pending:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"{len(pending)} of {len(rows)} candidates need validation -> {PENDING.relative_to(ROOT)}")
    for r in pending:
        print("  ", r["id"])


def cmd_record(results: list[str], dataset: str | None) -> None:
    rows = {r["id"]: r for r in load_rows(Path(dataset) if dataset else PENDING)}
    done = load_hashes()
    added, failed = 0, []
    for path in results:
        for res in load_rows(Path(path)):
            name = res.get("name")
            if name not in rows:
                continue
            if res.get("valid") is True:
                done[name] = row_hash(rows[name])
                added += 1
            else:
                failed.append((name, res.get("reason"), (res.get("error") or "")[:80]))
    HASHES.write_text(json.dumps(dict(sorted(done.items())), indent=1) + "\n", encoding="utf-8")
    print(f"recorded {added} valid; {len(done)} validated in total; not valid: {failed or 'none'}")


def main() -> None:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("write")
    rec = sub.add_parser("record")
    rec.add_argument("results", nargs="+")
    rec.add_argument("--dataset", help="dataset file the results came from (default: the pending file)")
    args = ap.parse_args()
    if args.cmd == "write":
        cmd_write()
    else:
        cmd_record(args.results, args.dataset)


if __name__ == "__main__":
    main()
