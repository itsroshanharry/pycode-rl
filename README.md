# PyCode-RL

This repository holds three things:
- **A Python coding environment** for Prime Intellect's [verifiers](https://github.com/PrimeIntellect-ai/verifiers)
  v1, published on the Environments Hub as
  [`itsroshanharry/pycode-env`](https://app.primeintellect.ai/dashboard/environments/itsroshanharry/pycode-env).
- **The pipeline that built and validated its 75 tasks.**
- **A hosted multi-model leaderboard and a null vs `bash` harness comparison run on it.**

| Read this | For |
|---|---|
| [`environments/pycode/README.md`](environments/pycode/README.md) | The environment: tasks, harnesses, leaderboard, how to run it, grader design, caveats. This is the page shown on the Hub. |
| [`REPORT.md`](REPORT.md) | The full report: funnel, verifier design, every leaderboard table, findings F1-F12, costs, limitations, evidence index. |
| [`NOTES.md`](NOTES.md) | The day-by-day decision log (newest first): every decision, number, cost reading and mistake as it happened. |

## In one minute

- **Tasks.** 75 single-function Python tasks (38 `train` / 37 `test`), each grounded in a real-world
  rule: date conventions, protocol details, billing and tax rules, config dialects and the like.
  About 2,200 hidden pytest cases.
- **Grading.** A hardened grader in a Prime sandbox. The candidate runs in an unprivileged worker,
  isolated from the trusted pytest process. 19 reward-hacking and broken submissions all score 0.
- **Two harnesses:**
  - `null`, the default: no tools, and the reply's code block is graded;
  - `bash`: the model writes and tests `/work/solution.py`, which is graded in a fresh sandbox.
- **How the tasks were checked:**
  1. seed-grounded synthesis;
  2. spec and test checks: mutation score, coverage, a spec lint, and gold and no-op checks in
     a sandbox;
  3. a difficulty filter with triage of the never-solved tasks;
  4. decontamination against HumanEval, MBPP and LiveCodeBench (n-gram check plus LLM judges);
  5. an audit by models from other families;
  6. a split that keeps tasks tuned on model attempts out of `test`.
  - Funnel: 100 written -> 81 after the difficulty filter -> 75 final.

**Leaderboard** (hosted, all 75 tasks x 4 attempts, temperature 1.0, reasoning `low`, 16k max tokens, `null` harness):

| Model | pass@1 (95% CI, tasks) | pass^4 | Hard tasks (23) |
|---|---|---|---|
| `deepseek/deepseek-v4.1-flash-1017` | 0.940 (0.90-0.97) | 0.853 | 0.880 |
| `google/gemma-4-31b-it` | 0.740 (0.65-0.82) | 0.613 | 0.359 |
| `openai/gpt-oss-120b` | 0.523 (0.43-0.61) | 0.293 | 0.109 |
| `openai/gpt-oss-20b` (difficulty-filter model) | 0.380 (0.30-0.46) | 0.107 | 0.054 |

- 0 infrastructure errors in 1,200 attempts.
- Every pair of neighbouring models differs with a paired 95% CI that excludes 0.
- **No tools vs bash** (20 pre-registered hard tasks):
  - gpt-oss-120b went from 0.45 to 0.30 with tools: false "file written" claims, and calls to a
    tool that does not exist here (`apply_patch`);
  - Nemotron 3.5 Super went from 0.725 to 0.75, and truncation dominates its failures.

**Findings worth reading** (all in [REPORT.md](REPORT.md)):
- **F1:** a token cap, not the model, decided the first pilot.
- **F3:** a second model found spec defects that self-checks cannot see.
- **F9:** tools did not help, and gpt-oss-120b got worse.
- **F10:** hosted runs rebuild tasks from their data, and a run-time guard caught a silent grading
  bug before any score was recorded.
- **F11:** the triage-kept hard tasks are where the top models separate.

## Repository layout

```
environments/pycode/        the published verifiers v1 package (flat layout)
  pycode_env/taskset.py       taskset, tasks (reply and file mode), harness guard
  pycode_env/grader/          run_pytest.py: PEP 723 grader script, threat model in its docstring
  pycode_env/data/            dataset.jsonl (the 75 final tasks, sha256 119ed403...)
  README.md                   the Hub page
tasks/handwritten/          10 early examples (spec, reference, tests, mutants, meta)
tasks/generated/<batch>/    90 generated candidates in 9 batches (b01-b09), same file format
pipeline/                   offline pipeline scripts, numbered by stage (below)
pipeline/prompts/           seeds.jsonl (102 seed rules), generate_v1/v2/v3.md (versioned prompts)
data/                       intermediate datasets (candidates -> filtered -> decontaminated -> dataset)
data/reports/               evidence for every claim: validation, difficulty, pilots, contamination,
                            review, split, leaderboard, harness (raw traces gzipped)
tests/                      grader cheat suite, early-example checks, taskset option and guard tests
.devcontainer/              the GitHub Codespace used for all Linux-only steps
CLAUDE.md                   the project instructions given to Claude Code
REPORT.md, NOTES.md         report and decision log
```

## Pipeline

| Stage | Script | What it does |
|---|---|---|
| 0 | `00_build_handwritten.py` | early examples -> dataset rows |
| 1 | `01_assemble_candidates.py` | `tasks/generated/` -> `data/candidates.jsonl` |
| 2 | `02a_local_check.py` | free: reference passes, at least 2 of 3 authored mutants fail, naive solutions time out (Linux, root) |
| 2 | `02b_test_strength.py` | free: automatic AST mutation score >= 0.80, branch coverage >= 0.90, a docstring-only fake fails (Linux, root) |
| 2 | `lint_spec_traps.py` | spec lint: test traps the spec does not state; docstrings that break copied solutions |
| 2 | `02c_pending.py` | runs paid `vf-validate` (gold and no-op checks in Prime sandboxes) only on new or changed candidates |
| 3 | `03_difficulty.py` | difficulty filter (gpt-oss-20b x 8) and the triage bookkeeping |
| 4 | `04_contamination.py` | fetch pinned benchmark corpora, n-gram check, LLM judge, decisions |
| 5 | `05_split_export.py` | stratified split (seed 2026) and export to the package |
| 6 | `06_review.py` | audit by other-family models; summary of verdicts |
| - | `07_leaderboard.py`, `07b_regrade.py` | fetch hosted traces, compute statistics; re-grade stored attempts |
| - | `08_harness_compare.py` | null vs bash: pre-registered selection, launch, ingest, compare |
| - | `pilot_summary.py`, `quick_selfcheck.py`, `taskfiles.py` | helpers |

Each script's docstring gives its exact usage.

## Reproducing

- **Python 3.12 with [uv](https://docs.astral.sh/uv/).** `uv sync` installs the workspace. Two pins
  in the root `pyproject.toml`:
  - `verifiers` is pinned to commit `20c549f`, the version inside Prime's hosted-eval runner;
  - the environment package is installed in editable mode.
- **Linux is required** for `vf-run` / `vf-validate` and for the grader checks (verifiers' runtimes
  import `fcntl`). The `.devcontainer/` folder defines the Codespace used here.
- **Run the grader tests as root**, so that the worker drops privileges as it does in a sandbox:
  `sudo .venv/bin/python -m pytest tests`. 51 tests pass.
- **Paid steps** (inference, sandboxes) need a Prime account and `PRIME_API_KEY`; see
  `.env.example`. Never commit a key.
- **The whole project cost about $6.84** from a $10 wallet. The cost of each stage is in
  REPORT.md.
- **Hosted evaluation**, as on the leaderboard:
  ```bash
  prime eval run itsroshanharry/pycode-env --hosted -m <model> -n -1 -r 4 -c 8 \
    -a '{"taskset": {"split": "all"}}' \
    -S '{"temperature": 1.0, "reasoning_effort": "low", "max_tokens": 16384}'
  ```
  The `bash` variant and all options are in the
  [environment README](environments/pycode/README.md#how-to-run).
- **Re-analysing the leaderboard** uses only the committed data, with no model calls:
  `uv run python pipeline/07_leaderboard.py analyze`.

## How this was built

- **Tasks and code.** The tasks and the pipeline code were produced with Claude Code (Claude Opus
  5.5), under the project owner's direction. The commit messages carry a `Co-Authored-By` line to
  show this.
- **Checks.** One model writing a task's spec, tests and reference can misread a rule the same way
  in all three. The later stages exist to catch that:
  - automatic checks;
  - attempts and reviews by models from other families (gpt-oss, DeepSeek);
  - the owner's spot-check.
- **Model choices.** Claude is not on the leaderboard.
- **Instructions.** `CLAUDE.md` is the instruction file the work followed, including its budget
  and safety rules: no model-written code runs outside Prime sandboxes, and spending is capped.

Limitations are listed in [REPORT.md](REPORT.md#limitations).

## License

MIT. See [LICENSE](LICENSE).
