# pycode-env

Single-turn Python function-implementation tasks. The model receives a function
specification (signature, docstring, examples) and replies with code; the code is graded
by a hidden pytest suite inside a Prime sandbox. Reward is 1.0 iff every hidden test passes.

**Dataset (v0.2.0): 75 tasks, 38 `train` / 37 `test`.** The tasks are grounded in real-world
rules (date/time formats, protocols such as HTTP caching and cookies, checksums, billing and
payroll rules, config formats, scheduling), not textbook puzzles.

## Usage

```bash
# hosted evaluation (all tasks, as on our leaderboard)
prime eval run itsroshanharry/pycode-env --hosted -m <model> -r 4 -c 8 \
  -a '{"taskset": {"split": "all"}}' \
  -S '{"temperature": 1.0, "reasoning_effort": "low", "max_tokens": 16384}'
# local
uv run vf-run pycode-env --env.taskset.split test -n 5 -r 1 -m <model>
```

Taskset options: `split` = `train` | `test` | `all` (default `test`).
Task options: `call_timeout` (default 5 s per call), `total_timeout` (default 60 s per solution).
Reasoning models need a generous `max_tokens`: some tasks need more than 8k thinking tokens.

## How the tasks were made

AI-generated (Claude Code, through versioned prompts), each grounded in a real-world "seed"
rule, then filtered by independent checks:

| Stage | Kept | What was checked |
|---|---|---|
| Written | 100 | 90 generated + 10 hand-written |
| Validation | 100 | reference passes, authored and automatic mutants are killed (mutation score >= 0.8), branch coverage >= 0.9, hard-coded answers fail, gold/no-op checks in a Prime sandbox |
| Difficulty filter | 81 | `openai/gpt-oss-20b`, 8 attempts per task: tasks solved 8/8 were dropped as too easy; tasks solved 0/8 were kept only if a stronger model solved them |
| Contamination | 75 | exact n-gram overlap against HumanEval, MBPP and LiveCodeBench (no 13-gram shared with any problem), two LLM judges for reworded or well-known contest problems (6 dropped), plus a web-verified author review |
| Audit | 75 | every task reviewed by an independent model (spec vs tests vs reference), 1 major + 2 minor defects fixed; 8 tasks spot-checked by a human |

Each task's `meta` records its difficulty band, filter pass rate, generator and prompt version.
The `train` split holds every task that was changed after seeing model results; `test` holds
only tasks nobody tuned on.

## Design

- **Harness:** `null` by default (no tools). Shared scoring in the same sandbox. The sandbox has no network access once the agent starts.
- **Hidden tests:** stored as extra `TaskData` fields. They never appear in the prompt and are written into the sandbox only for grading.
- **Grader** (`grader/run_pytest.py`): trusted pytest runs in one process; the candidate runs in a separate worker that:
  - runs as an unprivileged user;
  - has rlimits, per-call and total timeouts, and fd-level silenced output;
  - talks to the test process over a JSON plain-data protocol (no pickle).

  This defeats the cheats we tested: rigged `__eq__` objects, printing fake results, patching pytest, `sys.exit`/`os._exit`, reading the hidden tests, and killing the grader. A grade from a non-isolated worker is refused.
- **Validation** (`vf-validate`): the reference must pass every test, at least 2 of 3 mutants must fail, and an untouched task must score 0.
- **Metrics** besides the reward: fraction of tests passed, no-code, load errors and call timeouts, so failures can be traced to the model, the harness (e.g. truncation) or the task.

## Limitations

- Hidden tests are bundled in this package and recorded in traces: hidden from the model, but not secret.
- Single function per task, fully specified; strong reasoning models solve most tasks, so the spread between models is largest at the mid tier.
- The difficulty filter used one model (`gpt-oss-20b`), so difficulty is calibrated to it.
- Contamination checks against LeetCode-style sites rely on LLM judges' memory (no public corpus).
- 75 tasks: about ±11 points per-model confidence intervals on the full set.
