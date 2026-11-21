# pycode-env

**Real-world specification-following tasks for Python code generation.** Each task is one
function grounded in a real rule: a date or time convention, a protocol detail (HTTP caching,
cookies, content negotiation), a checksum, a billing, payroll or tax rule, a config dialect, a
scheduling policy. The model gets the signature and a precise docstring and writes the code.
The code is graded by a hidden pytest suite inside a Prime sandbox, using a hardened grader.

Puzzle benchmarks test recall of known algorithms. These tasks test what everyday engineering
needs: reading a precise spec carefully and implementing every rule, edge case and error
condition correctly.

- **75 tasks** (38 `train` / 37 `test`), 73 distinct topics, about 2,200 hidden test cases
  (median 27 per task).
- **Difficulty-calibrated:** tasks a reference model always solved were removed. Tasks it never
  solved were kept only after a stronger model solved them or a review confirmed the spec.
- **Decontaminated** against HumanEval, MBPP and LiveCodeBench (a model-free n-gram check plus
  LLM judges), and audited task by task by models from other families (DeepSeek, OpenAI).
- **Hardened grader:** 19 reward-hacking and broken submissions all score 0.
- **Supports two harnesses:** `null` (no tools; the model replies with code) and `bash` (the
  model writes and tests a file; that file is graded in a fresh sandbox). See below.

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

## Two harnesses: `null` (no tools) and `bash`

The same 75 tasks and the same hidden tests work with either harness. Only how the model works
and how it hands in its answer differ.

| | `null` harness (default) | `bash` harness |
|---|---|---|
| What the model can do | Read the task and reply once. No tools. | Run shell commands and edit files for several turns. It can run and test its own code. |
| How it hands in the answer | A ```python code block in its reply (`taskset.solution: reply`, the default) | The file `/work/solution.py` (`taskset.solution: file`) |
| Where the answer is graded | In the same sandbox, after the reply. Safe, because the model never touched it. | In a fresh sandbox that receives only `solution.py`. Anything else the agent left in its own sandbox cannot affect the grade. |
| Settings | None needed | `agent.harness.id: bash` and `taskset.solution: file`, together |
| Hosted runs | Yes (the leaderboard below) | Yes (tested with a hosted run) |

The environment refuses a tool harness combined with `solution: reply`. That combination would
grade inside the sandbox the agent had a shell in, so the attempt fails with an error before the
model is called. Commands for both setups are in [How to run](#how-to-run).

## Leaderboard (no tools)

All 75 tasks, 4 attempts per task, temperature 1.0, reasoning effort `low`, `max_tokens` 16384,
`null` harness. Hosted Prime evaluations; 0 infrastructure errors in 1,200 attempts.

| Model | pass@1 (95% CI) | pass@4 | pass^4 | Tests passed | Truncated | Model $ per task |
|---|---|---|---|---|---|---|
| `deepseek/deepseek-v4.1-flash-1017` | **0.940** (0.90-0.97) | 0.987 | 0.853 | 0.978 | 2.0% | 0.0119 |
| `google/gemma-4-31b-it` | **0.740** (0.65-0.82) | 0.827 | 0.613 | 0.977 | 0.0% | 0.0075 |
| `openai/gpt-oss-120b` | **0.523** (0.43-0.61) | 0.720 | 0.293 | 0.937 | 0.0% | 0.0041 |
| `openai/gpt-oss-20b` (difficulty-filter model, calibration row) | **0.380** (0.30-0.46) | 0.680 | 0.107 | 0.855 | 0.0% | 0.0015 |

- **pass@1:** the chance one attempt passes every hidden test. The 95% CI comes from a
  task-level bootstrap.
- **pass@4:** solved at least once in 4 attempts. **pass^4:** solved on all 4 attempts
  (reliability).
- **Tests passed:** the mean fraction of hidden tests passed. It stays high where pass@1 drops
  because many wrong answers are near misses (at least 90% of tests passed): 74% of Gemma's
  and 66% of gpt-oss-120b's wrong answers. Gemma's often miss the stated validation and
  error rules.
- **Model $ per task:** model fees for 4 attempts.
- **The ranking is robust:** every adjacent pair differs with a paired, per-task 95% CI that
  excludes 0. The order is the same on the 37 `test` tasks alone (0.946 / 0.764 / 0.541 /
  0.392), on `train`, and on the hardest tasks.
- **Calibration row:** difficulty was calibrated with `gpt-oss-20b`, so its row is labelled. The
  filter removed tasks it always solved.
- **Grader version:** all scores use grader v3 and dataset `119ed403`. During the runs we found
  and fixed a grader bug: valid code that uses a `@dataclass` with string type annotations
  failed to load. Grader v3 fixes it and adds a regression test. The bug affected 1 of the 600
  attempts graded before the fix. That attempt was re-graded with v3 and still fails, so no
  score changed.

Hosted runs that are shared from the Prime dashboard appear on this environment's Leaderboard
tab.

## No tools vs the `bash` harness

Do tools help on these tasks? The `bash` harness gives the model a shell, so it can write
`/work/solution.py`, run it and fix it. We compared it with the no-tools setting on 20 hard
tasks. The tasks were chosen before any bash attempt: a random 20 (seed 2026) of the 53 tasks
the filter model solved at most half the time. Each model had 2 bash attempts per task and at
most 16 turns, with the same sampling settings as the leaderboard.

| Model | No tools pass@1 | Bash pass@1 | Paired difference (95% CI) | Model $ per attempt |
|---|---|---|---|---|
| `openai/gpt-oss-120b` | 0.45 | **0.30** | -0.15 (-0.31 to +0.01) | 0.0011 -> 0.0053 |
| `nvidia/nemotron-3.5-super-vl` | 0.725 | 0.75 | +0.025 (-0.15 to +0.18) | 0.0051 -> 0.0073 |

- **Tools did not help either model.**
  - Both mostly re-ran the docstring examples. Those examples do not reach the edge cases and
    rules the hidden tests check.
- **gpt-oss-120b got worse, for two reasons.**
  - In 7 of 40 attempts it tested its code in a throwaway script, never saved the file, and
    then replied that the file was written.
  - In 26 of 40 attempts it first called `apply_patch`, a file-editing tool from a different
    harness that does not exist here.
- **Nemotron's failures are mostly truncation** in both settings: it writes about 10k output
  tokens per answer.
- **Scale:** neither difference is statistically clear at 20 tasks x 2 attempts.
- **How the runs were made:** with local `vf-run`, using the commands below. The no-tools
  baseline for gpt-oss-120b is its leaderboard attempts on the same 20 tasks. All 80 bash
  attempts were graded in a fresh sandbox, with 0 infrastructure errors.

## How to run

Results of a hosted run appear in your Prime dashboard (Evaluations and Prime Traces), and you
can share them to the Leaderboard tab. Hosted runs always use the latest version of this
environment. A local `vf-run` writes results only to its output folder (`-o`).

### No tools (default)

```bash
# hosted: the leaderboard settings
prime eval run itsroshanharry/pycode-env --hosted -m <model> -n -1 -r 4 -c 8 \
  -a '{"taskset": {"split": "all"}}' \
  -S '{"temperature": 1.0, "reasoning_effort": "low", "max_tokens": 16384}'

# local (verifiers v1, Linux)
prime env install itsroshanharry/pycode-env
uv run vf-run pycode-env -m <model> -n 5 -r 1 --env.taskset.split test \
  --sampling.temperature 1.0 --sampling.reasoning-effort low --sampling.max-tokens 16384
```

### `bash` harness (the 20-task comparison)

Always pair a tool harness with `solution: file`. The default `reply` mode grades in the
agent's own sandbox, which is safe only without tools. The environment refuses a tool harness
in `reply` mode: the attempt fails with an error before the model is called.

```bash
# hosted
prime eval run itsroshanharry/pycode-env --hosted -m <model> -n -1 -r 2 -c 8 \
  -a '{"agent": {"harness": {"id": "bash"}, "max_turns": 16},
       "taskset": {"split": "all", "solution": "file", "ids": ["pc-c-0001", "pc-c-0013",
         "pc-c-0014", "pc-c-0019", "pc-c-0032", "pc-c-0033", "pc-c-0039", "pc-c-0047",
         "pc-c-0050", "pc-c-0054", "pc-c-0055", "pc-c-0061", "pc-c-0062", "pc-c-0063",
         "pc-c-0064", "pc-c-0066", "pc-c-0069", "pc-c-0073", "pc-c-0088", "pc-hw-005"]}}' \
  -S '{"temperature": 1.0, "reasoning_effort": "low", "max_tokens": 16384}'

# local
uv run vf-run pycode-env -m <model> -r 2 \
  --env.agent.harness.id bash --env.agent.max-turns 16 --env.taskset.solution file \
  --env.taskset.split all --env.taskset.ids pc-c-0001 pc-c-0013 pc-c-0014 pc-c-0019 \
    pc-c-0032 pc-c-0033 pc-c-0039 pc-c-0047 pc-c-0050 pc-c-0054 pc-c-0055 pc-c-0061 \
    pc-c-0062 pc-c-0063 pc-c-0064 pc-c-0066 pc-c-0069 pc-c-0073 pc-c-0088 pc-hw-005 \
  --sampling.temperature 1.0 --sampling.reasoning-effort low --sampling.max-tokens 16384
```

### Options

Hosted runs pass these in `-a` as JSON (for example `{"taskset": {"split": "all"}}`). Local
runs pass them as `--env.<name>` flags, with `_` written as `-`.

| Option | Values | Default |
|---|---|---|
| `taskset.split` | `train`, `test`, `all` | `test` |
| `taskset.ids` | a list of task ids. Every id must exist in `split`, so use `split: all` for a mixed list | empty (all tasks) |
| `taskset.solution` | `reply`: grade the reply's last code block. `file`: grade `/work/solution.py` in a fresh sandbox | `reply` |
| `agent.harness.id` | `null` (no tools), `bash` (requires `solution: file`) | `null` |
| `agent.max_turns` | turn limit for tool harnesses (the comparison used 16) | set by the harness |
| `taskset.task.call_timeout` | seconds per call into the solution | 5 |
| `taskset.task.total_timeout` | seconds for all calls into one solution | 60 |

**Token budget:** give reasoning models at least 16k `max_tokens`. Six tasks need more than 8k
thinking tokens even for a strong model, and a low cap measures truncation, not ability. In our
pilot, a 2k cap cut DeepSeek's score from 0.90 to 0.44, and every failure was a cut-off reply.

## How the tasks were built

**Funnel:**
1. 100 candidates written.
2. 100 pass the spec and test checks.
3. 81 remain after the difficulty filter and triage.
4. 75 remain after decontamination.
5. 75 after the audit (3 fixed).
6. Split into 38 `train` / 37 `test`.

**Who did what.** The tasks and the pipeline code were produced with Claude Code (Claude Opus
5.5), under the project owner's direction. When one model writes a task's spec, hidden tests and
reference solution together, it can misread a rule the same way in all three, and its own
self-checks would still pass. The later stages are there to catch that. They are automatic
checks, attempts and reviews by models from other families, and a spot-check by the project
owner. Every keep, drop and fix decision was recorded with its reason.

### 1. Writing: seed-grounded synthesis (100 candidates)

This follows the idea of OSS-Instruct (Magicoder; Wei et al., 2023). Asking a model for problems
from a blank prompt drifts towards LeetCode clones, so every task is grounded in a *seed*: one of
102 short real-world rules in 11 categories (dates, text formats, business rules, scheduling,
networking, identifiers, numeric, data cleaning, structured data, games, text). OSS-Instruct
grounds problems in open-source code snippets. Here the grounding is a real-world rule, which
yields specification-heavy tasks instead.

90 candidates were generated from three versioned prompts, in batches of 10. 10 earlier
examples were written while the grader was built, and 2 of them are in the final set. Each task
has:
- a spec;
- a reference solution;
- the hidden tests;
- 3 deliberately buggy variants (mutants);
- metadata (topic, levers, prompt version, and the seed for generated tasks);
- for efficiency tasks, a naive slow solution.

Prompts v2 and v3 (58 of the final tasks) build in difficulty "levers":

- **twist:** a familiar problem with one changed rule, so a memorized answer fails;
- **combo / composition:** two techniques that must work together;
- **spec-trap:** an easily misread rule. It is always stated in the spec and always tested;
- **layered rules, exactness:** interacting rules with stated precedence, and exact arithmetic;
- **efficiency:** stated input limits, a large-input test, and a naive solution that must time
  out.

### 2. Spec and test checks (100 of 100 pass)

**Writing rules for specs and tests:**
- A test may only check what the spec states. Every error rule is tested with its exact
  exception type.
- Many test files include a differential test: an independent oracle (a simpler or
  brute-force method) checks the solution on 100-500 seeded random inputs. The v3 prompt
  requires one for hard tasks.
- Since v3, non-trivial expected values come from that oracle, not from hand arithmetic, which
  had been wrong more than 10 times in earlier batches.

**Spec lint.** A pilot found 4 tests that rejected inputs the spec allowed, for example
full-width digits where the spec said only "digits". A lint (a script that scans for known
problems) now flags:
- tests with non-ASCII inputs when the spec never says ASCII;
- `bool` inputs when the spec never mentions bool;
- docstring text that breaks a solution which copies the docstring, such as a triple quote.

Each hit is reviewed. The 4 specs were fixed to state the rule.

**Test strength.** These checks are free, run in a Linux container with the real grader:
- the reference passes every test;
- at least 2 of the 3 mutants fail;
- an automatic AST mutation score of at least 0.80;
- branch coverage of the reference of at least 0.90;
- a fake solution that only returns the docstring answers fails;
- for efficiency tasks, the naive solution times out.

The automatic mutants found 20 real test gaps, which were fixed.

**Prime sandbox (`vf-validate`).** The reference scores 1.0 (gold check) and an untouched task
scores 0 (no-op check). This was run again on the frozen final dataset: 75 of 75 pass.

### 3. Difficulty filter (100 -> 81)

- `gpt-oss-20b` made 8 attempts per task: temperature 1.0, reasoning effort `low`, an 8k-token
  cap, 0% truncated.
- Number of tasks solved k of 8 times, for k = 0..8: 25, 9, 7, 6, 7, 7, 12, 8, 19.
- Tasks solved 1-7 times out of 8 were kept. The 19 tasks solved 8/8 were dropped as too easy.

### 4. Triage of the 25 never-solved tasks

A task that no attempt solves is either hard or broken. Each of the 25 got one attempt by a
stronger model, `deepseek-v4.1-flash`:
- **17 were solved.**
- **6 were cut off at 8k tokens, and all 6 were solved at 16k.** These tasks need long thinking,
  which is why the leaderboard uses a 16k cap.
- **2 failed and were reviewed against their specs by Claude Code:**
  - One had a spec defect: a triple quote in a docstring example broke every solution that
    copied the docstring. It was fixed, the lint rule above was added, and the task was
    re-filtered: solved 2/8, so it was kept.
  - In the other, every model misses one rule that the spec states explicitly. It was kept as
    hard and flagged for the audit.

Result: 57 tasks in the 1-7 band and 24 hard tasks. A hard task is hard but solvable, not broken.

### 5. Decontamination (81 -> 75)

**(a) Model-free n-gram check.**
- Every task was compared with each of 2,193 benchmark problems, at pinned revisions:
  HumanEval (164), MBPP (974) and LiveCodeBench (1,055, all 6 releases).
- It compares normalized-token 5-gram Jaccard similarity and the longest common token run, on
  the prompt and on the reference code.
- Drop thresholds: Jaccard 0.5, or a shared 13-gram.
- Result: the highest similarity was 0.011 for prompts and 0.073 for code, with no shared
  13-gram.

**(b) LLM judge.** `gpt-oss-20b` (temperature 0) saw each task with its 3 most similar benchmark
problems from (a). It answered two questions:
- Is this the same problem reworded?
- Is it a well-known LeetCode or Codeforces-style problem, and which one?

It found 0 reworded copies and flagged 6 tasks as well-known. 5 were dropped. 1 was overruled:
the judge cited a LeetCode problem that does not exist, and the task implements the RFC 3339
timestamp rule.

**(c) Second pass during the audit.**
- The audit models answered the same "well-known?" question.
- Claude Code also checked all remaining tasks for resemblances using web searches. This pass
  is not independent.
- 1 more task was dropped: same input and output as LeetCode 1943.
- 1 flag was overruled: the standard natural-sort snippet fails 6 of 15 of that task's test
  groups.

In total, 6 tasks were dropped as well-known problems and 2 flags were overruled with evidence.
The judges' citations were often wrong even when their yes/no answer was right, so every flag
was checked against the actual problem.

### 6. Audit (75 tasks, 3 fixed)

- Every task was reviewed by a model from a different family than the writer: DeepSeek V4.1
  Flash (31 tasks) or `gpt-oss-120b` (44).
- Each reviewer compared the spec, tests and reference, looking for ambiguity, tests that check
  unstated rules, and reference bugs.
- 6 tasks were flagged:
  - 3 were fixed and re-validated. The one major defect fixed: the tests accepted input that
    the spec did not allow.
  - 3 were dismissed with reasons.
- The project owner then spot-checked 8 randomly chosen tasks.

### 7. Split

The 6 tasks whose specs were edited because of how models failed on them are all in `train`, so
no `test` task was tuned on model attempts. The remaining tasks were stratified by difficulty
band and prompt version (seed 2026).

## Grader and anti-hacking design

- **No tools by default:** the `null` harness gives the model no tools. It writes code and the
  code is graded. The sandbox (`python:3.11-slim`, 1 vCPU, 1 GiB) has no network access once
  the agent starts.
- **Hidden tests:** stored as `TaskData` fields that never enter the prompt. They are written
  into the sandbox only at grading time, after the model has finished.
- **Isolated execution:** trusted pytest runs in one process. The candidate runs in a separate
  worker that:
  - runs as an unprivileged user, so it cannot read the tests;
  - has memory, file and process limits, plus per-call and total timeouts;
  - has its output silenced at the file-descriptor level;
  - exchanges only plain data (JSON, no pickle).
- **File mode for tool harnesses:**
  - The agent's sandbox is never used for grading, because a shell could have planted files
    there that fake a pass.
  - Only `/work/solution.py` is copied into a fresh sandbox with no network access, and it is
    graded there.
  - A marker file written in the agent's sandbox proves that the grading sandbox is a
    different one. If the marker is found, grading stops with an error instead of a score.
  - The mode is stored in each task's data, so hosted runs, which rebuild every task from its
    data, grade the same way as local runs.
- **Verified against 19 reward-hacking and broken submissions**, which all score 0:
  - rigged objects: `__eq__` that always returns true, int subclasses;
  - fake grader output: printing a fake result, patching pytest and `assert`;
  - exiting early: `sys.exit`, `os._exit` or `KeyboardInterrupt`, during import or inside a call;
  - reading the hidden tests, writing a `conftest.py`;
  - killing the grader, infinite loops, memory bombs, oversized return values;
  - hard-coding the examples;
  - broken replies: empty code, syntax errors, a wrong function name.
- **Correct reward semantics:** a wrong answer scores 0, but an infrastructure fault or a
  misconfigured run raises an error, so these are never recorded as model failures.

**Reward:** `passed_all_tests` (1.0 if every hidden test passes).

**Diagnostic metrics:**
- `frac_tests_passed`, `no_code`, `load_error` and `call_timeouts`.
- Each trace also records the first failing test, so a failure can be traced to the model
  (wrong answer, crash, timeout), the harness (a truncated reply) or the task.
- In file mode, `solution_source` records where the graded code came from:
  - `file`: the file the agent wrote;
  - `reply_fallback`: the reply's code block, used when no file was written;
  - `none`: no code at all.

## Scope and caveats

- **Scope:** self-contained functions with complete specifications. The environment measures
  careful implementation of precise rules. It does not measure repository navigation or
  multi-file changes.
- **Test visibility:** as in HumanEval and most open code benchmarks, the hidden tests ship
  inside the package. They are hidden from the model, not from people who install it. Do not
  train on the `test` split if you report results on it.
- **Difficulty calibration:** difficulty was calibrated with one model (`gpt-oss-20b`). It
  appears on the leaderboard as a labelled calibration row.
- **One writing model:** the tasks come from one model family (Claude), so they share its style
  and blind spots. Claude is not on the leaderboard, so no listed model is scored on tasks it
  wrote.
- **Well-known problems:** there is no public corpus of LeetCode or Codeforces problems, so
  resemblance to them was checked with LLM judges and web searches.
- **Comparing models:** with 75 tasks, compare models with paired, per-task differences rather
  than by overlapping intervals.
- **The bash comparison is small:** 2 models, 20 tasks, 2 attempts each. It shows how tool use
  can fail on these tasks; it does not establish that tools never help.

Dataset sha256 `119ed403e4977450209a44a3c2d99e7661fd0c17611c9525b7e8f1d182fc2680`.
