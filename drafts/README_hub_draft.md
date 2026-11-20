# pycode-env

**Real-world specification-following tasks for Python code generation.** Each task is one
function grounded in a real rule: a date or time convention, a protocol detail (HTTP caching,
cookies, content negotiation), a checksum, a billing, payroll or tax rule, a config dialect, a
scheduling policy. The model gets the signature and a precise docstring and replies with code.
The code is graded by a hidden pytest suite inside a Prime sandbox, using a hardened grader.

Puzzle benchmarks test recall of known algorithms. These tasks test what everyday engineering
needs: reading a precise spec carefully and implementing every rule, edge case and error
condition correctly.

- **75 tasks** (38 `train` / 37 `test`), 73 distinct topics, about 2,200 hidden test cases
  (median 27 per task).
- **Difficulty-calibrated:** tasks a reference model always solved were removed. Tasks it never
  solved were kept only if a stronger model proved them solvable.
- **Decontaminated** against HumanEval, MBPP and LiveCodeBench (model-free n-gram check plus LLM
  judges), and audited task by task by a model other than the author.
- **Hardened grader:** 19 reward-hacking and broken submissions all score 0.

## Example task (train split)

```python
def fiscal_label(date: str, start_month: int) -> str:
    """Fiscal year and quarter label such as "FY2025-Q3".

    The fiscal year starts on day 1 of `start_month` (1..12) and is named after the
    calendar year in which it ENDS: with start_month = 4, April 2024 through March
    2025 is FY2025. [...] Raise ValueError for a malformed or invalid date, or a
    start_month that is not an int in 1..12.

    >>> fiscal_label("2024-05-10", 4)
    'FY2025-Q1'
    """
```

The familiar shape hides a rule change ("named after the year in which it ends") and strict
input validation. `gpt-oss-20b` solved it 0 of 8 times; `deepseek-v4.1-flash` solved it.

## Leaderboard

<!-- DRAFT: filled in from data/reports/leaderboard/summary.json after the 0.2.0 runs finish -->

All 75 tasks, 4 attempts per task, temperature 1.0, reasoning effort `low`, `max_tokens` 16384,
`null` harness (no tools). pass@1 is shown with a task-level bootstrap 95% CI. pass^4 means
the task was solved on all 4 attempts (reliability).

| Model | pass@1 (95% CI) | pass@4 | pass^4 | truncated | $ per task |
|---|---|---|---|---|---|
| `deepseek/deepseek-v4.1-flash-1017` | | | | | |
| `openai/gpt-oss-120b` | | | | | |
| `google/gemma-4-31b-it` | | | | | |
| `openai/gpt-oss-20b` (difficulty-filter model; calibration row) | | | | | |
| `qwen/qwen3.5-9b` | | | | | |

## Usage

```bash
# hosted evaluation (the leaderboard settings)
prime eval run itsroshanharry/pycode-env --hosted -m <model> -n -1 -r 4 -c 8 \
  -a '{"taskset": {"split": "all"}}' \
  -S '{"temperature": 1.0, "reasoning_effort": "low", "max_tokens": 16384}'

# local run (verifiers v1)
uv run vf-run pycode-env --env.taskset.split test -n 5 -r 1 -m <model>
```

| Option | Values | Default |
|---|---|---|
| `taskset.split` | `train`, `test`, `all` | `test` |
| `call_timeout` | seconds per function call | 5 |
| `total_timeout` | seconds per solution | 60 |

**Token budget:** give reasoning models at least 16k `max_tokens`. Six tasks need more than 8k
thinking tokens even for a strong model. A low cap measures truncation, not ability. In our
pilot, a 2k cap cut DeepSeek's score from 0.90 to 0.44, and every failure was a cut-off reply.

## How the tasks were built

**Seed-grounded synthesis.** This follows the idea of OSS-Instruct (Magicoder; Wei et al., 2023).
Asking a model for problems from a blank prompt drifts towards LeetCode clones, so every task
is grounded in a *seed*: one of 102 short real-world rules in 11 categories (dates,
text formats, business rules, scheduling, networking, identifiers, numeric, data cleaning,
structured data, games, text). OSS-Instruct grounds problems in open-source code snippets.
Here the grounding is a real-world rule, which yields specification-heavy tasks instead.

73 tasks were written by Claude Code (Claude Opus 5.5) from three versioned generation
prompts, and 2 are hand-written. Prompts v2 and v3 (58 tasks) build in difficulty "levers":

- **twist:** a familiar problem with one changed rule, so a memorized answer fails;
- **combo / composition:** two techniques that must work together;
- **spec-trap:** an easily misread rule. It is always stated in the spec and always tested;
- **layered rules, exactness:** interacting rules with stated precedence, and exact arithmetic;
- **efficiency:** stated input limits, a large-input test, and a naive solution that must time
  out.

Each task records its seed, topic, levers and prompt version in `meta`.

**Every task then had to pass checks that do not depend on the author's judgment:**

| Stage | Kept | Checks |
|---|---|---|
| Written | 100 | 90 generated + 10 hand-written |
| Test strength | 100 | The reference passes. At least 2 of 3 authored buggy variants (mutants) fail. An automatic AST mutation score of at least 0.80. Branch coverage of at least 0.90. A fake that only returns the docstring answers fails. Efficiency tasks: the naive solution times out. Gold and no-op checks run in a Prime sandbox (`vf-validate`). The automatic mutants found and fixed 20 real test gaps. |
| Difficulty filter | 81 | `gpt-oss-20b`, 8 attempts per task. 19 tasks solved 8/8 were dropped as too easy. **Triage:** each of the 25 tasks solved 0/8 got an attempt by a stronger model (`deepseek-v4.1-flash`). 23 were solved, 6 of them only with a 16k-token budget. The 2 failures were inspected by hand: one had a spec defect, which was fixed and re-filtered; the other was kept after review. A "hard" task is therefore hard but solvable, not broken. |
| Decontamination | 75 | **Model-free n-gram check** against 2,193 problems from HumanEval, MBPP and LiveCodeBench (all releases, pinned revisions), on both prompts and solutions. Highest 5-gram Jaccard similarity: 0.011 for prompts, 0.073 for code. No shared 13-gram. **LLM judges**, with the most similar benchmark problems as context, checked for reworded copies and well-known contest problems; every flag was reviewed by hand. 6 tasks were dropped as well-known problems. 2 flags were overruled, each with evidence: one judge invented a problem citation; for another, the standard snippet for the claimed "classic kata" fails 6 of 15 test groups. |
| Audit | 75 | Every task was reviewed by a model other than the author (DeepSeek V4.1 Flash or gpt-oss-120b), comparing spec, tests and reference for ambiguity, unstated checks and reference bugs. 3 defects were fixed and re-validated. Then 8 tasks were spot-checked by a human. |

**Split.** The 6 tasks whose specs were edited because of how models failed on them are all in
`train`, so no `test` task was tuned on model attempts. The remaining tasks were stratified by
difficulty band and prompt version (seed 2026).

## Grader and anti-hacking design

- **Harness:** `null` by default, so the model has no tools. It writes code and the code is graded.
  The sandbox (`python:3.11-slim`, 1 vCPU, 1 GiB) has no network access once the agent starts.
- **Hidden tests:** stored as `TaskData` fields that never enter the prompt. They are written
  into the sandbox only at grading time.
- **Isolated execution:** trusted pytest runs in one process. The candidate runs in a separate
  worker that:
  - runs as an unprivileged user;
  - has memory, file and process limits, plus per-call and total timeouts;
  - has its output silenced at the file-descriptor level;
  - exchanges only plain data (JSON, no pickle).
- **Verified against 19 reward-hacking and broken submissions**, which all score 0:
  - rigged objects: `__eq__` that always returns true, int subclasses;
  - fake grader output: printing a fake result, patching pytest and `assert`;
  - exiting early: `sys.exit`, `os._exit` or `KeyboardInterrupt`, during import or inside a call;
  - reading the hidden tests, writing a `conftest.py`;
  - killing the grader, infinite loops, memory bombs, oversized return values;
  - hard-coding the examples;
  - broken replies: empty code, syntax errors, a wrong function name.
- **Correct reward semantics:** a wrong answer scores 0, but an infrastructure fault raises an
  error, so grader failures are never recorded as model failures.

**Reward:** `passed_all_tests` (1.0 if every hidden test passes).

**Diagnostic metrics:** `frac_tests_passed`, `no_code`, `load_error` and `call_timeouts`. Each
trace also records the first failing test, so a failure can be traced to the model (wrong
answer, crash, timeout), the harness (a truncated reply) or the task.

## Scope and caveats

- **Scope:** self-contained functions with complete specifications. The environment measures
  careful implementation of precise rules. It does not measure repository navigation or
  multi-file changes.
- **Test visibility:** as in HumanEval and most open code benchmarks, the hidden tests ship
  inside the package. They are hidden from the model, not from people who install it. Do not
  train on the `test` split if you report results on it.
- **Difficulty calibration:** difficulty was calibrated with one model (`gpt-oss-20b`). It
  appears on the leaderboard as a labelled calibration row.
- **Well-known problems:** there is no public corpus of LeetCode or Codeforces problems, so
  resemblance to them was checked with LLM judges and manual web verification.
- **Comparing models:** with 75 tasks, compare models with paired, per-task differences rather
  than by overlapping intervals.

Dataset sha256 `119ed403e4977450209a44a3c2d99e7661fd0c17611c9525b7e8f1d182fc2680`.
<!-- DRAFT: add the pipeline repository link here if it is made public -->
