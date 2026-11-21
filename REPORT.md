# PyCode-RL: report (DRAFT)

Status: draft, built up as the project runs. Every number here must be backed by a file in
`data/reports/`; the final version is written after the leaderboard.

**Update 2026-11-21.** The leaderboard and the null vs bash comparison are done.
- New sections were added: Environment summary, Verifier design, Leaderboard results, F11-F12,
  Process lessons, Costs, Limitations and Evidence index.
- Nothing written earlier was removed or reworded. Sections recorded while the project ran
  keep their original text, and later corrections are added as notes beside them.
- The day-by-day decision log, with every intermediate number, is `NOTES.md` (newest entry
  first).

## Contents

| Planned item | Where it is |
|---|---|
| 1. What the environment is | [Environment summary](#environment-summary) |
| 2. How the tasks were made | [Environment summary](#environment-summary); per-stage detail in the Hub README (`environments/pycode/README.md`) and NOTES.md |
| 3. Funnel | [Funnel (so far)](#funnel-so-far) |
| 4. Verifier design and reward-hack tests | [Verifier design and reward-hack tests](#verifier-design-and-reward-hack-tests) |
| 5. Leaderboard | [Leaderboard results](#leaderboard-results-hosted-2026-11-20-to-2026-11-21); [Failure-mode analysis](#failure-mode-analysis-notes-for-the-leaderboard-chapter-recorded-2026-11-21) |
| 6. Harness comparison | [F8 probes](#f8-bash-harness-probes-2026-11-21-tool-use-costs-differ-a-lot-by-model-and-harness-fit-matters); [F9 results](#f9-null-vs-bash-harness-2026-11-21-tools-did-not-help-and-gpt-oss-120b-got-worse); [F10 hosted fix](#f10-hosted-runs-rebuild-tasks-from-data-a-run-time-guard-caught-a-silent-grading-bug-2026-11-21) |
| 7. Findings | [F1-F7](#findings-to-include-collected-as-they-happen); F8-F10 above; [F11](#f11-the-hard-triaged-tasks-are-where-the-top-models-separate); [F12](#f12-cost-estimates-missed-the-hosted-runner-sandbox); [Process lessons](#process-lessons) |
| 8. Limitations | [Limitations](#limitations) |
| (added) Costs | [Costs](#costs) |
| (added) Evidence | [Evidence index](#evidence-index) |

## Planned structure
1. What the environment is (single-turn Python function tasks, hidden tests, isolated grader).
2. How the tasks were made (seed-grounded synthesis in the spirit of OSS-Instruct; prompt versions v1-v3).
3. Funnel with rejection counts at every stage.
4. Verifier design and reward-hack tests.
5. Leaderboard (Wilson 95% CIs, pass@k, pass^k, failure modes, cost per task).
6. Harness comparison (null vs bash; stretch).
7. Findings, including harness-vs-model attributions.
8. Limitations.

## Environment summary

**Environment.** `itsroshanharry/pycode-env` on the Prime Environments Hub (verifiers v1, PRIVATE as of
2026-11-21). Flat package `environments/pycode/pycode_env/`. Its wheel holds:
- `taskset.py`;
- `grader/run_pytest.py`, a PEP 723 script that pins `pytest==8.4.2`;
- `data/dataset.jsonl`.

**Dataset.**
- 75 tasks: 38 `train` / 37 `test`.
- sha256 `119ed403e4977450209a44a3c2d99e7661fd0c17611c9525b7e8f1d182fc2680`.
- 73 distinct topics; about 2,200 hidden test cases, median 27 per task.
- Each row holds: `id`, `split`, `prompt`, `entry_point`, `tests` (hidden), `reference`, `mutants`, `meta`.

**Task format.**
- One pure function over plain data, specified by a signature and a docstring with examples.
- The model is told to use Python 3.11 and only the standard library.

**Sandbox per task.**
- Image `python:3.11-slim`; 1 vCPU, 1 GiB memory, 5 GiB disk.
- Timeouts: setup 300 s, agent 600 s, finalize 180 s, scoring 60 s.
- Network policy `allow=[]`, applied after setup. Setup still installs pytest for the grader.
- Grader limits: 5 s per call into the candidate (`call_timeout`) and 60 s for all calls
  (`total_timeout`).

**Reward and metrics.**
- Reward: `passed_all_tests` (weight 1.0; 1.0 only if every hidden test passes).
- Metrics (in `grading_details`): `frac_tests_passed`, `no_code`, `load_error`, `call_timeouts`.
- Each trace also stores the full grade in `trace.info["grade"]`: passed, total, failed,
  errors, load_error, timeouts, crashes, isolated, first_failure, grader version.

**Two harnesses** (both work in hosted runs since 0.2.3):

| | `null` (default) | `bash` |
|---|---|---|
| Model's tools | none | shell and file edits for several turns (`agent.max_turns`, 16 in our runs) |
| Answer | the last fenced code block of the reply, after removing `<think>` text (`taskset.solution: reply`) | `/work/solution.py` (`taskset.solution: file`) |
| Grading | in the same sandbox, after the reply (shared scoring) | in a fresh sandbox that receives only `solution.py` (isolated scoring, artifact) |

**Options:**

| Option | Values and default |
|---|---|
| `taskset.split` | `train` / `test` / `all`; default `test` |
| `taskset.ids` | list of task ids; default empty, meaning all tasks |
| `taskset.solution` | `reply` / `file`; default `reply` |
| `taskset.dataset_path` | load another JSONL; used by the pipeline |
| `taskset.task.call_timeout`, `taskset.task.total_timeout` | grader time limits |
| `agent.harness.id` | `null` / `bash`; default `null` |

**How the tasks were made** (detail per stage in the Hub README and in NOTES.md):
- Seed-grounded synthesis in the spirit of OSS-Instruct, from 102 real-world seed rules in 11
  categories (`pipeline/prompts/seeds.jsonl`).
- Three versioned generation prompts:
  - `generate_v1.md`: batches b01-b02;
  - `generate_v2.md`: b03-b08, adding difficulty levers;
  - `generate_v3.md`: b09, harder by construction, with oracle-computed expected values.
- 90 candidates in 9 batches of 10, plus 10 earlier examples written while the grader was built.
- The tasks and the pipeline code were produced with Claude Code (Claude Opus 5.5), under the
  project owner's direction.
- Every later gate was automatic, or done by other models (gpt-oss-20b, DeepSeek V4.1 Flash,
  gpt-oss-120b), or by the project owner's spot-check (8 tasks).

**Package versions on the Hub:**

| Version | Date | What changed |
|---|---|---|
| 0.1.0 | 2026-11-18 | first push (flat layout); hosted smoke test passed |
| 0.1.1 | 2026-11-18 | grader v2: plain-data codec and exception-rebuild fix |
| 0.2.0 | 2026-11-20 | frozen 75-task dataset `119ed403`, grader v2; leaderboard wave 1 ran on it |
| 0.2.1 | 2026-11-20 | grader v3 (the candidate module is registered, so `@dataclass` with string annotations works); wave 2 ran on it |
| 0.2.2 | 2026-11-21 | `taskset.ids`, the harness guard, the final Hub README |
| 0.2.3 | 2026-11-21 | hosted file-mode fix (F10): the mode is stored in the task data and the declared class is `PyCodeAnyTask` |
| 0.2.4 | 2026-11-21 | README only: the two-harness section, methods per stage, explicit attribution |

## Funnel (so far)
| Stage | Tasks in | Kept | Notes | Evidence |
|---|---|---|---|---|
| Generated + hand-written | - | 100 | 90 Claude-written (9 batches) + 10 hand-written | `tasks/` |
| Validation (02a/02b/vf-validate) | 100 | 100 | 20 real test gaps found by auto-mutants and fixed | `data/reports/validated_hashes.json` |
| Difficulty filter (gpt-oss-20b x 8) | 100 | 81 | 19 too easy (8/8); 25 at 0/8 triaged with DeepSeek, all kept (1 after a spec fix, 1 manual) | `data/reports/difficulty_final.json` |
| Contamination (lexical + 2 LLM judges + author web check) | 81 | 75 | lexical clean; 6 dropped as well-known problems, 1 judge flag overruled | `data/reports/contamination/decisions.json` |
| Audit (all 75: DeepSeek 31 + gpt-oss-120b 44; user spot-check 8) | 75 | 75 | 6 flagged: 1 major + 2 minor fixed, 3 dismissed (1 false positive); 1 'well-known' flag overruled with evidence | `data/reports/review/summary.json`, `decisions.json`, `spot_check.json` |
| Split | 75 | 38 train / 37 test | 6 tasks changed after seeing model results forced to train | `data/reports/split.json` |

**Stage details (added 2026-11-21).** The numbers come from NOTES.md and the evidence files.

- **Validation:**
  - `02a_local_check.py`: the reference passes, and at least 2 of the 3 authored mutants fail.
    Efficiency tasks: the naive `slow.py` times out.
  - `02b_test_strength.py`, checks that do not depend on the task writer:
    - automatic AST mutation score of at least 0.80 (operator swaps, and/or swaps, +-1 on
      integer constants, dropped `not`, statements replaced by `pass`);
    - branch coverage of the reference of at least 0.90;
    - a fake that returns only the docstring answers must fail.
  - `vf-validate` in Prime sandboxes, only for new or changed candidates (`02c_pending.py`):
    gold and no-op checks.
  - The frozen dataset was validated again in full: 75/75 (`data/reports/validate/`).
- **Spec lint** (`pipeline/lint_spec_traps.py`):
  - It flags non-ASCII or `bool` test inputs when the spec never says ASCII or bool, and
    triple quotes inside docstrings.
  - It was added after the 3-model pilot found 4 such spec defects (c0035, c0037, c0061, c0078).
    All 4 specs now state the rule.
  - The remaining 3 hits were reviewed and were false alarms.
- **Difficulty filter:**
  - gpt-oss-20b, 8 attempts per task; temperature 1.0, reasoning effort low, 8192-token cap.
  - 800/800 attempts ok, 0% truncated, about $0.37.
  - Number of tasks solved k of 8 times, for k = 0..8: 25, 9, 7, 6, 7, 7, 12, 8, 19.
  - Keep rate before triage: v1 14/20, v2 32/60, v3 5/10, early examples 5/10.
- **Triage of the 25 tasks solved 0/8** (DeepSeek V4.1 Flash, 1 attempt each):
  - 17 solved;
  - 6 truncated at 8192 and then all solved at 16384 (5.5k-13.6k tokens);
  - 2 failed and were reviewed against their specs:
    - c0004 had a triple quote in its docstring example (F4). It was fixed, the lint rule was
      added, and the task was re-filtered: 2/8, so it moved into the keep band.
    - c0036: every model misses its stated "export + SPACE (not tab)" rule. Kept as
      `hard_manual` and flagged for the audit.
  - Result: 57 in the filter band, 23 `hard_triage`, 1 `hard_manual` = 81.
- **Decontamination:**
  - (a) Lexical check, all 81 x 2,193 pairs. Corpora: HumanEval 164 (openai/human-eval @
    b9453e8), MBPP 974 (google-research @ f82046b), LiveCodeBench code_generation_lite, all 6
    releases, 1,055 problems (HF @ 0fe84c3). Highest 5-gram Jaccard: prompt 0.011, code 0.073
    (threshold 0.5). No shared 13-gram (longest common run 0).
  - (b) LLM judge, gpt-oss-20b at temperature 0, given each task and its top-3 similar
    benchmark problems; about $0.035. 0 "same problem reworded"; 6 "well-known" flags:
    - dropped: pc-hw-004 (LRU cache semantics), pc-hw-006 (interval-DP brackets),
      pc-c-0026 (meeting-rooms pattern), pc-c-0057 (point in polygon) and pc-c-0059 (Project
      Euler 109 darts; the judge said 170);
    - overruled: pc-c-0040 (the judge invented "Sort the Timestamps (LeetCode)"; the task is
      the RFC 3339 rule).
  - (c) During the audit:
    - DeepSeek flagged pc-hw-008 (same input and output shape as LeetCode 1943), and it was
      dropped.
    - gpt-oss-120b flagged pc-c-0022 as the "natural sort kata". This was overruled: the
      standard snippet fails 6 of 15 test groups.
    - Claude Code checked all 76 tasks with web searches and examined 10 resemblances: 1 drop
      (pc-hw-008) and 9 kept with notes. This check is labelled not independent.
- **Audit:**
  - `pipeline/06_review.py`. Each task got spec + tests + reference and four questions:
    well-known? ambiguous? unstated checks? reference bugs?
  - DeepSeek: $0.48, but 44 of 76 calls ran out of the 12k-token budget while still thinking.
    Those tasks were re-reviewed by gpt-oss-120b, giving final coverage DeepSeek 31 +
    gpt-oss-120b 44 = 75.
  - Verdicts: 69 ok, 4 minor, 2 major.
    - Fixed: c0028 (major: the tests accepted whitespace the spec did not allow), c0029
      (`B == 0` past the end now raises ValueError) and c0085 (type check). All three were
      re-validated.
    - Dismissed: c0005, c0079 (a non-int value is outside the stated input contract) and c0073.
  - The project owner spot-checked 8 tasks chosen with seed 8: c0008, c0014, c0022, c0023,
    c0032, c0037, c0058, c0060 (`data/reports/review/spot_check.json`).
- **Split:** seed 2026, stratified by difficulty band and prompt version. Tasks changed after
  their model results were seen are forced into train: c0004, c0035, c0036, c0037, c0061,
  c0078.
- **Dataset hashes:**
  1. `b5159e5f` (76 tasks, after contamination);
  2. `2fecc250` (split revised);
  3. `119ed403` (after the audit; frozen and used for every leaderboard run).

## Verifier design and reward-hack tests

**Task layer** (`environments/pycode/pycode_env/taskset.py`):
- `setup` creates `/work` and pre-installs the grader's dependencies with
  `runtime.prepare_uv_script`, while the network is still open.
- Reply mode: `finalize` extracts the last fenced code block, ignoring `<think>` text. With no
  code the grade is `no_code`, score 0. Otherwise it calls `_grade`.
- `_grade` writes the solution and the hidden tests into a fresh `uuid` folder, then runs the
  grader with `run_uv_script`.
- Fail closed:
  - a nonzero grader exit raises `RuntimeError` (an infrastructure or task fault, never a 0);
  - a grade with `isolated: false` (the worker could not drop privileges) raises instead of
    being trusted.
- The reward and the metric both read `trace.info["grade"]`, so grading runs once per attempt.

**Grader v3** (`grader/run_pytest.py`, threat model in its docstring):
- **Separate processes:** trusted pytest and the test file run in one process. The candidate
  runs in a separate worker behind a `solution` proxy module. So the candidate cannot patch
  pytest, rewrite reports, override `assert` or print a fake result.
- **Plain-data exchange:** replies are JSON with a tagged encoding of exact builtin types, never
  pickle. A rigged `__eq__` or an int/str subclass cannot cross the boundary.
- **Privileges and files:**
  - the worker runs as uid/gid 65534 (nobody);
  - the tests live in a 0700 root-owned temporary folder, and the input files are deleted on
    read;
  - the worker cannot read the tests, or signal or ptrace the grader.
- **Limits:**
  - rlimits on address space, file size 0, process count and core dumps;
  - per-call and total wall-clock timeouts;
  - the worker's stdin, stdout and stderr are /dev/null at the file-descriptor level;
  - `SystemExit`, `os._exit` and crashes kill only the worker, which restarts for the next test;
  - `PYTHONHASHSEED=0` in the worker.
- **History:**
  1. v1;
  2. v2 (0.1.1): a plain-data codec and an exception-rebuild fix, after a false negative;
  3. v3 (0.2.1): the candidate module is registered in `sys.modules`, so valid `@dataclass`
     code with string annotations loads.

**File mode** (`PyCodeFileTask`, routed by `PyCodeAnyTask`):
- **In the agent's sandbox, at the end of the attempt (`finalize`):**
  - writes a marker file, `/tmp/pycode-solver-sandbox`;
  - normalizes `/work/solution.py` into one plain file, replacing a symlink or a directory,
    and treating a file over 1,000,000 bytes as no code;
  - if no file was written, falls back to the reply's last code block (`reply_fallback`);
  - records `solution_source`.
- **In the grading sandbox (the metric, isolated scoring):**
  - refuses to grade if the marker exists (`shared`);
  - grades the restored file and records `graded_in_fresh_sandbox`.
- **Guard (`PyCodeEnv.run`):** a non-`null` harness with `solution: reply` raises before the
  agent runs.
- **Since 0.2.3 the mode is a data field**, `PyCodeData.solution` (F10).

**Test suite.** It runs in the Codespace as root, so the worker drops privileges as it does in a
Prime sandbox. 51 tests pass:
- `tests/test_grader.py` (28):
  - 19 cheat and broken submissions that must score 0: `always_equal_object`, `empty`,
    `hardcoded_examples`, `huge_return_value`, `infinite_loop`, `infinite_loop_on_import`,
    `int_subclass_eq`, `kill_grader`, `memory_bomb`, `os_exit_in_call`,
    `patch_pytest_and_assert`, `print_fake_result`, `raise_keyboardinterrupt`,
    `raise_systemexit`, `read_hidden_tests`, `syntax_error`, `sys_exit_on_import`,
    `write_conftest`, `wrong_function_name`;
  - 5 legitimate solutions that must score 1: `custom_exception_subclass`,
    `late_stdlib_imports`, `module_introspection` (the v3 regression), `prints_and_sleeps`,
    `reference`;
  - 4 grader contract tests: cheat output cannot reach the grader's stdout; broken tests and an
    empty test file are grader errors, not zeros; a UnicodeDecodeError matches ValueError.
- `tests/test_handwritten.py` (10): reference passes and mutants fail, for the early examples.
- `tests/test_taskset_options.py` (13): `ids` selection and errors; the mode surviving a
  replica of the hosted rebuild; the guard; reply vs file routing with an in-memory fake
  runtime.

## Findings to include (collected as they happen)

### F1. The token cap, not the model, decided the first pilot (harness vs model)
DeepSeek V4.1 Flash on 20 tasks x 4: mean reward **0.44 at max_tokens 2048** vs **0.90 at
8192**. At 2048, 56% of rollouts were truncated and *every* failure was a cut-off (38 cut off
while reasoning with no code, 7 cut off mid-code); there were 0 wrong answers.
Evidence: `data/reports/pilot/pilot-20x4.json`, `pilot-20x4-8k.json`.

### F2. Qwen3.6-35B-A3B is excluded from the leaderboard because of its token budget
Qwen3.6 thinks about 7.6k tokens per answer even at reasoning_effort "low". It was
**truncated on 79% of rollouts at 8192 tokens** (pilot, 33 rollouts, mean reward 0.15), and
**about 25% still truncated at 16384** (probe: 12-16k tokens per answer). A fair cap would
need 24-32k tokens at about $0.015+ per attempt, about as much as the other four models
combined, so it was left out of the budget-limited leaderboard. Its low pilot score measures
the cap, not its ability. Lesson: report truncation next to every pass rate, and probe each
model's token use before a scaled run.
Evidence: `data/reports/pilot/pilot-20x4-8k-qwen-partial.json`, probe traces (NOTES.md).

### F3. A second model found spec defects that self-checks cannot see
Gemma 4 31B failed 4 tasks by exactly one test each because the tests rejected inputs the spec
never excluded ("digits" that had to be ASCII, "an int" that could not be a bool). The
reference, tests and checker shared the author's reading, so self-checks passed. Fixed; lint
added (`pipeline/lint_spec_traps.py`).

### F4. A task's own text broke valid solutions
c0004's docstring example contained a triple quote, so any solution that copied the docstring
failed to parse (DeepSeek 0/31 tests; gpt-oss 6/8 load errors). After the fix, gpt-oss solved
it 2/8. Added to the lint.

### F5. More rules did not make tasks harder for a strong reasoning model
generate_v3 (more interacting rules, stated precedence, exactness, explicit traps): DeepSeek
stayed at 0.90; gpt-oss-20b moved 0.475 -> 0.50. Fully specified single-function tasks seem to
saturate for this tier; the spread between models is at the mid tier.

### F6. LLM-judge contamination verdicts need human review of their reasons
The judge's yes/no was usually defensible, but it cited 2 wrong problem numbers (Project Euler
"170" for the darts task, which is PE 109) and invented one LeetCode problem.

### F7. Catalog listing is not availability
Two "Gateway" models (`poolside/laguna-s-2.1`, `qwen/qwen3-coder-next`) were listed by
`prime inference models` but returned 404 "no provider serves" / "No allowed providers".
The errors were recorded as provider errors, not model failures.

## Leaderboard results (hosted, 2026-11-20 to 2026-11-21)

**Setup** (identical for every model):
- `prime eval run itsroshanharry/pycode-env --hosted -m <model> -n -1 -r 4 -c 8 -a '{"taskset": {"split": "all"}}'
  -S '{"temperature": 1.0, "reasoning_effort": "low", "max_tokens": 16384}'`.
- All 75 tasks, 4 attempts each, `null` harness, reply mode.
- Pushes were frozen during each wave, because hosted runs use `@latest`.
- Every task had all 4 attempts scored: 300/300 per model and 1,200 in total, with 0
  infrastructure errors.

| Model | Eval ID | Wave | Package |
|---|---|---|---|
| `deepseek/deepseek-v4.1-flash-1017` | `sejc1ih370l7bvm63dlm8wrh` | 1 | 0.2.0 (grader v2) |
| `openai/gpt-oss-20b` | `d8jyud550zvxewm0bwmvv8ae` | 1 | 0.2.0 (grader v2) |
| `google/gemma-4-31b-it` | `u8ibo4fn19zn1n6901ehgwrb` | 2 | 0.2.1 (grader v3) |
| `openai/gpt-oss-120b` | `skz9xmsfrtskb92xtlje97n4` | 2 | 0.2.1 (grader v3) |

- Smoke tests before the waves: `nmzewnbjsxv66ytoe5xz43df` (0.2.0, gpt-oss-20b, 2 tasks) and
  `qlneer6pw368k6qfsavvcmxd` (0.2.1, grader 3).
- Grader v2 to v3: `pipeline/07b_regrade.py` re-graded the 1 wave-1 attempt that the bug could
  have affected. The reward did not change (`data/reports/leaderboard/regrade.json`).

**Analysis method** (`pipeline/07_leaderboard.py`):
- Per-attempt results come from Prime Traces (`prime traces list --run-id`).
- Wilson 95% CI over attempts.
- Task-level bootstrap 95% CI: 10,000 resamples, seed 2026.
- Unbiased pass@k = 1 - C(n-c, k) / C(n, k), and pass^k = C(c, k) / C(n, k), with n = 4.
- Paired per-task differences, also with a task bootstrap.

**All 75 tasks:**

| Model | pass@1 | Wilson CI (attempts) | Bootstrap CI (tasks) | pass@2 | pass@4 | pass^2 | pass^4 | Tests passed | Truncated |
|---|---|---|---|---|---|---|---|---|---|
| DeepSeek V4.1 Flash | 0.940 | 0.907-0.962 | 0.897-0.973 | 0.976 | 0.987 | 0.904 | 0.853 | 0.978 | 2.0% |
| Gemma 4 31B | 0.740 | 0.688-0.786 | 0.650-0.823 | 0.802 | 0.827 | 0.678 | 0.613 | 0.977 | 0.0% |
| gpt-oss-120b | 0.523 | 0.467-0.579 | 0.433-0.610 | 0.644 | 0.720 | 0.402 | 0.293 | 0.937 | 0.0% |
| gpt-oss-20b (filter model, calibration row) | 0.380 | 0.327-0.436 | 0.303-0.460 | 0.536 | 0.680 | 0.224 | 0.107 | 0.855 | 0.0% |

| Model | Tasks solved 0/1/2/3/4 of 4 times | Mean output tokens (reasoning) | Model $ total | Model $ per task | Attempt sandbox $ (estimate) |
|---|---|---|---|---|---|
| DeepSeek V4.1 Flash | 1 / 1 / 2 / 7 / 64 | 4,239 (3,662) | 0.8929 | 0.0119 | 0.1293 |
| Gemma 4 31B | 13 / 1 / 8 / 7 / 46 | 5,437 (4,477) | 0.5644 | 0.0075 | 0.5005 |
| gpt-oss-120b | 21 / 7 / 13 / 12 / 22 | 1,170 (311) | 0.3068 | 0.0041 | 0.0706 |
| gpt-oss-20b | 24 / 18 / 11 / 14 / 8 | 987 (220) | 0.1138 | 0.0015 | 0.0658 |

**Paired differences** (row model minus column model, all 75 tasks; mean, bootstrap 95% CI,
tasks better / worse / tied):

| Pair | Mean diff | 95% CI | Better / worse / tied |
|---|---|---|---|
| DeepSeek - Gemma | +0.200 | 0.127 to 0.280 | 27 / 2 / 46 |
| DeepSeek - gpt-oss-120b | +0.417 | 0.330 to 0.500 | 51 / 1 / 23 |
| DeepSeek - gpt-oss-20b | +0.560 | 0.480 to 0.640 | 66 / 1 / 8 |
| Gemma - gpt-oss-120b | +0.217 | 0.140 to 0.297 | 38 / 6 / 31 |
| Gemma - gpt-oss-20b | +0.360 | 0.280 to 0.443 | 52 / 5 / 18 |
| gpt-oss-120b - gpt-oss-20b | +0.143 | 0.073 to 0.213 | 33 / 10 / 32 |

**Subsets** (pass@1, with the bootstrap CI over tasks). The ranking is the same in every
subset.

| Subset | Tasks | DeepSeek | Gemma | gpt-oss-120b | gpt-oss-20b |
|---|---|---|---|---|---|
| all | 75 | 0.940 (0.897-0.973) | 0.740 (0.650-0.823) | 0.523 (0.433-0.610) | 0.380 (0.303-0.460) |
| test | 37 | 0.946 (0.878-0.993) | 0.764 (0.649-0.872) | 0.541 (0.412-0.662) | 0.392 (0.284-0.507) |
| train | 38 | 0.934 (0.875-0.980) | 0.717 (0.579-0.842) | 0.507 (0.382-0.632) | 0.368 (0.263-0.480) |
| filter band (solved 1-7 of 8 by gpt-oss-20b) | 52 | 0.966 (0.918-0.995) | 0.909 (0.841-0.962) | 0.707 (0.625-0.793) | 0.524 (0.438-0.611) |
| hard band (kept by triage) | 23 | 0.880 (0.793-0.957) | 0.359 (0.196-0.522) | 0.109 (0.022-0.207) | 0.054 (0.011-0.098) |

- **Paired CIs between neighbouring models** (DeepSeek-Gemma / Gemma-120b / 120b-20b):
  - test: +0.182 (0.081 to 0.291) / +0.223 (0.115 to 0.338) / +0.149 (0.047 to 0.257);
  - train: +0.217 (0.112 to 0.336) / +0.211 (0.112 to 0.316) / +0.138 (0.046 to 0.230);
  - filter band: +0.058 (0.005 to 0.120) / +0.202 (0.120 to 0.288) / +0.183 (0.087 to 0.274);
  - hard band: +0.522 (0.380 to 0.663) / +0.250 (0.098 to 0.413) / **+0.054 (-0.022 to
    0.130), the only neighbouring pair whose CI includes 0**.
- **Task-level extremes:** 5 tasks were solved 4/4 by all four models: pc-c-0002, pc-c-0008,
  pc-c-0022, pc-c-0025, pc-c-0090. No task went unsolved by every model. 29 tasks were never
  solved by at least one model. DeepSeek never solved 1 task.
- **Stability of the difficulty estimate (gpt-oss-20b retest):**
  - filter mean 0.342 (8 attempts per task, 8192 cap) against leaderboard mean 0.380 (4
    attempts, 16384 cap);
  - Pearson r = 0.843 across tasks (`summary.json` -> `filter_retest`).
- **Hub leaderboard:** it shows one row per evaluation shared from the dashboard. As of
  2026-11-21 only gpt-oss-120b's run is shared. Its columns are platform-defined: model,
  status, samples, reasoning effort, average reward, publisher and date.
- **Not run (budget):** the planned 5th row, `qwen/qwen3.5-9b` (wave 3 was dropped in favour of
  the bash comparison), and the cross-benchmark calibration run.
- Evidence: `data/reports/leaderboard/` holds `summary.json`, `leaderboard.md`, `runs.json`,
  `regrade.json`, `regrade-v3.results.jsonl` and `rollouts_<model>.jsonl.gz`.

## Failure-mode analysis (notes for the leaderboard chapter, recorded 2026-11-21)

Every failed attempt is put into one diagnostic category instead of a bare 0. The goal is to
show that a 0 is a real model limitation, not a harness or spec defect. The categories are
computed in `pipeline/07_leaderboard.py` (`failure_mode`). Precedence: infra error > pass >
truncated > no code > load error > call timeout > wrong answer.

| Category | What it means | Leaderboard counts (DeepSeek / Gemma / gpt-oss-120b / gpt-oss-20b, out of 300 attempts each) |
|---|---|---|
| Truncated | hit `max_tokens` before finishing the code (harness cap) | 6 / 0 / 0 / 0 |
| Load error | syntax error, a broken import, or a crash while the module loads | 0 / 0 / 1 / 8 |
| Call timeout | too slow on a call, e.g. a naive solution on an efficiency task | 0 / 0 / 0 / 3 |
| No code | empty or prose-only reply (a refusal) | 0 / 0 / 0 / 1 |
| Wrong answer | ran, but failed hidden tests (edge cases and spec traps) | 12 / 78 / 142 / 174 |
| Infra error | sandbox or grader failure (raised, never scored as 0) | 0 / 0 / 0 / 0 |

### Harness vs model: evidence to cite
- **Token cap artifact (F1):** DeepSeek at max_tokens 2048 scored 0.44, against 0.90 at 8192.
  At 2048, **56% of all attempts** were truncated and **every** failure was a cut-off. Qwen3.6
  was truncated on **79% of attempts** at 8192 (F2). (These are shares of all attempts. An
  external summary called them shares of failures, which is wrong.)
- **Spec-ambiguity traps (F3):** Gemma exposed 4 tasks whose tests rejected inputs the spec
  never excluded (non-ASCII digits, a bool passed as an int). Fixed; `pipeline/lint_spec_traps.py`
  now flags this class.
- **Grader bug (grader v2 -> v3):** valid code using a `@dataclass` with string type annotations
  failed to load. Found by inspecting load errors one by one; it hit 1 of 600 wave-1 attempts.
  That attempt was re-graded with v3 and still fails, so no score changed. Its failure label
  stays "load error" (from the v2 grade), because the re-grade reports only pass or fail.
- **Infrastructure:** 0 infra errors and 0 lost attempts in all 1,200 leaderboard attempts
  (not only in the gpt-oss-20b run).
- **The small categories were checked by hand:**
  - load errors: 7 model syntax errors and 2 broken regular expressions at import, plus the
    c0001 grader-bug attempt;
  - timeouts: 2 on c0039, an efficiency task whose naive solution must time out (the trap
    working), and 1 infinite loop on c0004;
  - no code: 1 refusal on a benign unit-conversion task (gpt-oss-20b).

### Wrong answers are mostly near misses, and where they fail differs by model
| Model | Wrong answers | Near misses (>= 90% of tests passed) | First failing test: examples / validation / other |
|---|---|---|---|
| DeepSeek | 12 | 11 | 3 / 4 / 5 |
| Gemma 31B | 78 | 58 (74%) | 17 / 43 / 18 |
| gpt-oss-120b | 142 | 94 (66%) | 50 / 52 / 40 |
| gpt-oss-20b | 174 | 64 (37%) | 90 / 33 / 51 |

- Gemma usually gets the core logic right and misses the **stated validation and error
  rules**, which are what the spec traps target.
- gpt-oss-20b fails the **basic examples** more often, so its core logic is wrong more often.
- Caveat: "first failing test" depends on test order (examples usually come first), so this
  is a rough view. These two columns were a one-off analysis (2026-11-21); add them to
  `07_leaderboard.py` before the final chart.

### Task design around realistic failure modes
- Tasks target realistic failure modes instead of random puzzles: rule precedence (layered
  rules), multi-mode parsing, exact arithmetic, efficiency under stated limits, and stated spec
  traps (off-by-one boundaries, a bool passed as an int, non-ASCII digits, float precision,
  tab vs space). See prompts v2 and v3.

### Link to the null vs bash comparison
- Mid-tier models mostly fail by missing a few edge-case tests in single-turn mode. For example,
  gpt-oss-20b has pass@4 0.68 but pass^4 0.11, and gpt-oss-120b has 66% near misses.
- That makes them good candidates for the question: does a shell, where the model can run its
  own tests, reduce wrong answers and load errors?
- Measure the failure-mode shift per model, not only the score.

## F8. Bash-harness probes (2026-11-21): tool use costs differ a lot by model, and harness fit matters

Setup:
- `vf-run` in the Codespace, `--env.agent.harness.id bash --env.taskset.solution file`, max 16 turns.
- Sampling as on the leaderboard: temperature 1.0, reasoning effort low, max_tokens 16384.
- 2 tasks (c0014, c0033) x 1 bash attempt per model, plus a no-tools regression check and a
  Qwen no-tools baseline (2 tasks x 2 attempts).
- Total about $0.07. Traces are in `outputs/probes/` (git-ignored).

Mechanics:
- All 6 bash attempts were graded in a fresh sandbox; the solver-marker check passed.
- No errors and no truncation.
- In 5 of 6 attempts the model wrote `/work/solution.py`. Once, gpt-oss-120b replied with a
  code block instead, and the fallback graded that block.
- The default no-tools path still grades normally after the refactor (gpt-oss-20b, c0014: 23 of 24 tests).

| Model | Task | No tools | Bash result | Turns | Tool calls (apply_patch / ran own code) | Input tokens (cached) | Output tokens | Model $ per attempt |
|---|---|---|---|---|---|---|---|---|
| gpt-oss-120b | c0014 | 3/4 (leaderboard) | pass, 24/24 | 5 | 4 (2 / 1) | 3.6k (8.3k) | 3.0k | 0.0061 |
| gpt-oss-120b | c0033 | 1/4 (leaderboard) | pass, 27/27 (reply fallback) | 2 | 1 (1 / 0) | 1.7k (0.6k) | 2.0k | 0.0023 |
| gpt-oss-20b | c0014 | 2/4 (leaderboard) | fail, 0/24 (NameError `Solution`) | 5 | 4 (2 / 1) | 5.3k (9.9k) | 4.2k | 0.0041 |
| gpt-oss-20b | c0033 | 1/4 (leaderboard) | fail, 22/27 | 5 | 4 (0 / 0) | 2.6k (5.1k) | 2.0k | 0.0020 |
| qwen3.5-9b | c0014 | 0/2 (probe) | fail, 23/24 | 15 | 14 (0 / 10) | 4.2k (96k) | 8.4k | 0.0175 |
| qwen3.5-9b | c0033 | 0/2 (probe; 1 truncated at 16k) | pass, 27/27 | 12 | 11 (0 / 8) | 7.4k (102k) | 10.8k | 0.0195 |

Findings:
- **Tool-loop cost varies about 4x between models.** Qwen 9B works the way an agent should: it
  writes the file, runs it and fixes it over 12-15 turns. But it rereads about 100k tokens of
  (mostly cached) context and writes 8-11k tokens per attempt, about $0.019 against
  $0.002-0.006 for gpt-oss. A pairing with Qwen would have exceeded the budget cap, so the
  proposed bash comparison uses gpt-oss-120b and gpt-oss-20b. Qwen would be excluded for cost, not performance.
  - *Note added later:* the final pairing was gpt-oss-120b + Nemotron 3.5 Super (user decision, 2026-11-21),
    giving two model families of about the same size instead of two gpt-oss sizes. A Nemotron probe showed it is
    served, uses the tools, never calls `apply_patch`, and costs about $0.003 per bash attempt. Results: F9.
- **Harness fit:** both gpt-oss models first call `apply_patch`, the file-editing command of
  the Codex harness they were trained with. It does not exist in this sandbox.
  - In 5 of 8 gpt-oss tool calls on c0014/c0033, the model then recovered with `cat > file`
    or a Python writer.
  - Once (gpt-oss-120b, c0033) it gave up on the tools and answered with a code block.
  - gpt-oss ran its own code 0-1 times per attempt, against Qwen's 8-10.
  - So part of a bash-vs-null difference for gpt-oss can be harness mismatch rather than the
    value of tools. Measure it per attempt in the main run (apply_patch attempts, test runs).
- gpt-oss-20b's 0/24 on c0014 was its own bug: the module referenced an undefined `Solution`
  (a LeetCode-style class habit), not a grading problem.

## F9. Null vs bash harness (2026-11-21): tools did not help, and gpt-oss-120b got worse

Setup:
- The pre-registered 20 tasks (`data/reports/harness/selection.json`: random, seed 2026,
  from the 53 tasks with filter pass rate <= 0.5).
- 2 bash attempts per task: `--env.agent.harness.id bash --env.taskset.solution file`,
  max 16 turns, isolated scoring.
- Sampling as on the leaderboard.
- No-tools baselines:
  - gpt-oss-120b: its leaderboard attempts (4 per task);
  - Nemotron 3.5 Super (not on the leaderboard): its own run (2 per task).
- Local `vf-run` in the Codespace, so there is no platform record (see limitations). Cost
  $0.79 (model fees $0.71). All 80 bash attempts were graded in a fresh sandbox; 0 infra errors.
- Analysis: `pipeline/08_harness_compare.py`, `data/reports/harness/summary.json`.

| Model (both about 120B MoE) | No tools pass@1 | Bash pass@1 | Paired diff (95% CI, tasks) | Tasks better / worse | Model $ per attempt (no tools -> bash) |
|---|---|---|---|---|---|
| gpt-oss-120b | 0.45 | **0.30** | -0.15 (-0.31 to +0.01) | 2 / 7 | 0.0011 -> 0.0053 (5x) |
| Nemotron 3.5 Super | 0.725 | 0.75 | +0.025 (-0.15 to +0.18) | 5 / 3 | 0.0051 -> 0.0073 (1.4x) |

Why:
- **gpt-oss-120b: false completion claims plus a harness mismatch.**
  - In 7 of 40 attempts (17.5%) it ran its solution inside a throwaway `python - <<'PY'`
    script, never wrote `/work/solution.py`, and then replied "Implemented X in
    /work/solution.py". That is a claim of success without the work. Those attempts score 0.
  - 26 of 40 attempts first called the non-existent Codex `apply_patch` command (0.88 calls
    per attempt), then recovered.
  - Even when it delivered a file, it passed only 12 of 33 (0.36, against 0.45 without tools).
  - Its tests were mostly the docstring examples, which do not reach the edge cases and spec
    traps the hidden tests check. It also thought less per answer: about 640 output tokens per
    turn, against about 1,240 in one no-tools reply.
- **Nemotron: tools changed nothing.**
  - Its failures are mostly truncation in both modes (6/40 no tools, 4/40 bash, at 16k tokens
    per response). It thinks about 10k tokens per answer; `reasoning_effort` is not a listed
    parameter for it and appears to be ignored.
  - Leaving truncated attempts out, both modes are about 0.83-0.85.
  - It ran its own code more (2.3 calls per attempt) and never tried `apply_patch`.
- **Interpretation:**
  - On fully specified single-function tasks, an act -> observe -> debug loop only helps if
    the model writes tests for the spec's rules. Both models mostly re-checked the examples.
  - For gpt-oss, harness fit (`apply_patch`) and agentic reliability (claiming to have saved
    a file) cost more than the tools gave.
  - Neither difference is statistically clear at 20 tasks x 2 attempts. gpt-oss-120b's CI
    barely includes 0.

Limitations:
- 2 models, 20 tasks, 2 bash attempts.
- Same sampling settings but a different delivery (file vs reply).
- `max_turns` 16 (1 Nemotron attempt hit it).
- These local runs have no platform record, unlike the hosted leaderboard runs.
- Cost: estimated $0.57 from the probes, actual $0.79, because Nemotron's thinking per attempt
  in the full run was longer than in the 2-task probe. Probes this small under-estimate
  long-tail token use.

## F10. Hosted runs rebuild tasks from data; a run-time guard caught a silent grading bug (2026-11-21)

- **What happened:** the first hosted bash run (0.2.2, smoke test `bqwkoajiiurkbz6zviyw1q0t`) failed in 3 seconds
  with the environment's own guard error: "harness 'bash' gives the agent tools: add solution file". The run
  had asked for `solution: file`.
- **Cause:** hosted evals run through prime-rl's env server. It receives only each task's data and rebuilds the
  task as the class the taskset declares (`EnvServer._build_task`). The environment chose the file-mode class
  per task inside `load()`, which works locally but is lost in hosted runs.
- **What the guard prevented:** without it, the hosted run would have graded the reply's code block inside the
  agent's own sandbox, ignored the solution file and skipped the fresh-sandbox check. The scores would have looked
  normal and been both wrong and open to tampering.
- **Fix (0.2.3):** the mode is now a data field, and one declared task class routes to the reply or file
  behaviour from it. Tests replicate the server's rebuild step.
- **Lessons:**
  - In verifiers v1, everything that differs per task must be in `TaskData`, not in the Python class.
  - Check invariants at run time where they are used, not only at configuration time.
  - Test the hosted path, not just the local one.
- **Verification after the fix:**
  - Codespace test suite: 51 passed.
  - Local real runs: reply mode 30/30, and bash file mode 30/30 with `solution_source=file`
    and `graded_in_fresh_sandbox=true`.
  - Hosted smoke test `oqimyvumyopakf92d7cayxzv` on 0.2.3: completed, 0 errors. Trace
    `c9cf04ea37d348acb4a386ac7a457742` shows task type `PyCodeAnyTask`, `solution_source=file`
    and `graded_in_fresh_sandbox=true`. It passed 28/30 tests, so reward 0: a model miss on
    `test_invalid`, not an infrastructure fault. It again tried `apply_patch` first.
  - Cost of the smoke tests and checks: about $0.03.

## F11. The hard (triaged) tasks are where the top models separate

- **On the 52 filter-band tasks** (solved 1-7 of 8 by gpt-oss-20b), DeepSeek and Gemma are close:
  0.966 against 0.909, paired +0.058 (CI 0.005 to 0.120).
- **On the 23 hard tasks kept by triage** (0/8 for the filter model, solved by a stronger model):
  - DeepSeek scores 0.880 and Gemma 0.359, paired +0.522 (CI 0.380 to 0.663);
  - both gpt-oss models are at or below 0.11, with pass^4 = 0.
- **So triage did more than rescue tasks.** Without the "hard but solvable" tasks, the
  environment would barely separate the two strongest models.
- **At the bottom it is the reverse:** gpt-oss-120b vs gpt-oss-20b is separated on the filter
  band (+0.183) but not on the hard band (+0.054, CI includes 0).
- Evidence: `data/reports/leaderboard/summary.json` (`by_subset`).

## F12. Cost estimates missed the hosted runner sandbox

- The leaderboard was estimated at about $2.5 and cost about $3.42: wallet $7.5228 before wave
  1, $4.1001 after wave 2.
- Every hosted evaluation runs in its own runner sandbox at about $0.286/hr, for the whole run,
  on top of the per-attempt sandboxes. For example, wave 2: Gemma's runner ran 6,841 s ($0.544)
  and gpt-oss-120b's ran 1,023 s ($0.081).
- Slow models therefore cost more in runner time as well as in tokens.
- Model fees from the traces add up to $1.878. The estimated attempt sandboxes add up to $0.766.
- The bash study was estimated at $0.57 and cost $0.79, because the 2-task probe
  under-estimated Nemotron's long-tail thinking (F9).
- Lesson: estimate model fees, attempt sandboxes and the runner sandbox separately, and treat
  small probes as a lower bound.

## Process lessons

Recorded in NOTES.md as they happened. Each one became a working rule.
- **Probe every new kind of call, not only new models.**
  - The first audit pass (DeepSeek) cost $0.48, but 44 of 76 calls ran out of the 12k-token
    budget while still thinking.
  - Scripts now save each result as it finishes, and no spend guard may destroy partial
    results.
- **Probe every new model before a multi-attempt run.**
  - Qwen3.6's pilot was costed from DeepSeek's token use. It used 2.5x more and was stopped
    at 33/80 attempts.
- **Hand-computed expected values are an error source.**
  - They were wrong 6 times in one batch (format_number grouping, a base-36 constant, a
    polygon point, 3 overtime totals), and more than 10 times across b04-b08.
  - Each time the reference and an independent oracle agreed, and the hand value was the
    outlier.
  - generate_v3 bans hand arithmetic for non-trivial values.
- **Automatic mutants make the "strong tests" claim independent of the writer.**
  - They found 20 real test gaps that the authored mutants missed.
  - Surviving automatic mutants were inspected; the ones that remained were equivalent code.
  - The raw mutation score understates test strength by about 5 points on tasks with tag
    constants or redundant guards.
- **Timing-based checks need a large margin.**
  - Efficiency traps use a reference well under 1 s against a naive solution above 200 s, so
    machine speed cannot flip the result.
- **Environment pitfalls:**
  - verifiers' runtimes do not import on native Windows (`fcntl`), so every vf-* CLI ran in a
    GitHub Codespace;
  - the Codespace idle timeout is 10 minutes, so long runs needed a heartbeat;
  - `pgrep -f` / `pkill -f` match the ssh session's own command line;
  - Windows tools write CRLF line endings, so `.gitattributes` forces LF;
  - bash heredocs mangle quotes and backslashes in code (a regex in c0038, and one in
    `07_leaderboard.py`), so code files are written with the editor tool instead.
- **Develop against the hosted runner's verifiers commit** (`20c549f`, reported as
  0.4.1.dev150), not `main`.
- **Say where results will be visible.**
  - The bash comparison ran locally without the user being told that local runs leave no
    platform record. They had expected it on the leaderboard.
  - Every run proposal now states whether results land on the Prime dashboard and
    leaderboard, or only in local files.

## Costs

The project ran on one prepaid $10.00 wallet, with no auto top-up, a $7 spending cap and a $3
reserve. These wallet readings are from NOTES.md; inference billing posts in batches, so a
reading can lag by a few cents.

| Point in the project | Wallet | Spend so far |
|---|---|---|
| Start (2026-11-16) | $10.00 | $0.00 |
| After the first pilot (20 tasks x 4, 2026-11-20) | $9.603 | about $0.40 |
| After the 3-model pilot (about $0.97 across 4 runs) | $8.968 | about $1.03 |
| During the difficulty filter | $8.62 | about $1.38 |
| After the filter and triage | $8.10 | about $1.90 |
| After contamination (judge about $0.035) | $8.06 | about $1.94 |
| After the audit (DeepSeek review $0.48) | $7.58 | about $2.42 |
| Before leaderboard wave 1 | $7.5228 | about $2.48 |
| After wave 1 ($1.37: model fees $1.01, the rest sandboxes) | $6.1574 | about $3.84 |
| After wave 2 | $4.1001 | about $5.90 |
| After the bash probes (about $0.07) and the bash study ($0.79; model fees $0.71) | $3.189 | about $6.81 |
| After the 0.2.2-0.2.3 checks and both hosted smoke tests | $3.162 | **about $6.84** |

Total: about $6.84 of the $7 cap. 0 sandboxes were left running.

## Limitations

- **One writing model family:**
  - The tasks were produced with Claude Code, so they share one model's style and blind spots.
  - Claude is not on the leaderboard.
  - Per-generator pass rates (CLAUDE.md) could not be compared, because no second generator was
    used.
- **Difficulty was calibrated with one model, gpt-oss-20b, which is also on the leaderboard:**
  - its row is labelled as the calibration row;
  - its score is depressed by construction, because tasks it always solved were removed;
  - gpt-oss-120b is from the same family. This is disclosed.
- **Size:**
  - 75 tasks give task-bootstrap CIs of about ±4 points (DeepSeek) to ±9 points (gpt-oss-120b)
    per model on all tasks, and wider on the 37 test tasks;
  - the hard band has only 23 tasks.
- **Test visibility:**
  - the hidden tests ship inside the package; they are hidden from the model, not from people;
  - the test split has only 4 of the 9 final v3 tasks, because the pilot-checked tasks were
    forced into train. Final mix: v1 15 (8 test), v2 49 (24 test), v3 9 (4 test), early
    examples 2 (1 test).
- **Reviews:**
  - Some decisions were made by Claude Code: triage reviews, flag dismissals and overrules,
    and the web check for well-known problems, which is labelled not independent.
  - Independent checks are the other-family audit models and the owner's 8-task spot-check.
    The CLAUDE.md plan asked for a 40-task manual audit; the human sample is 8 tasks.
- **Mixed package versions:**
  - The leaderboard ran on two versions: 0.2.0 (grader v2) for wave 1 and 0.2.1 (grader v3)
    for wave 2.
  - The dataset was identical, and the one possibly affected attempt was re-graded with no
    change.
- **Sampling:**
  - one setting only: temperature 1.0, reasoning effort low, max_tokens 16384, one prompt
    format;
  - Nemotron appears to ignore `reasoning_effort`.
- **Failure analysis:**
  - "First failing test" depends on test order.
  - The near-miss and first-failing-test columns were a one-off analysis and are not yet
    produced by `07_leaderboard.py`.
- **Bash comparison:**
  - 2 models, 20 tasks, 2 attempts each;
  - run locally, so it has no platform record;
  - neither difference is statistically clear.
- **Not done:**
  - the cross-benchmark calibration (CLAUDE.md deliverable: compare model rankings with a
    public benchmark);
  - the planned qwen3.5-9b leaderboard row;
  - the optional upstream PR.

## Evidence index

| Claim area | Files |
|---|---|
| Tasks as written | `tasks/handwritten/`, `tasks/generated/<batch>/` (prompt.md, reference.py, tests.py, mutants.py, meta.json; slow.py for efficiency tasks) |
| Prompts and seeds | `pipeline/prompts/` (seeds.jsonl, make_seeds.py, generate_v1.md, generate_v2.md, generate_v3.md) |
| Validation | `data/reports/assemble.json`, `test_strength.json`, `validated_hashes.json`, `validate/` (final-validate.results.jsonl, summary.json) |
| Difficulty | `data/reports/difficulty.json`, `difficulty_final.json`, `difficulty/` (gzipped traces) |
| Pilots | `data/reports/pilot/` |
| Contamination | `data/reports/contamination/` (decisions.json, sources.json) |
| Audit | `data/reports/review/` (summary.json, decisions.json, spot_check.json) |
| Split | `data/reports/split.json`, `data/dataset.jsonl` (= the packaged `pycode_env/data/dataset.jsonl`) |
| Leaderboard | `data/reports/leaderboard/` (summary.json, leaderboard.md, runs.json, regrade.json, regrade-v3.results.jsonl, rollouts_*.jsonl.gz) |
| Harness comparison | `data/reports/harness/` (selection.json, summary.json, rollouts_*.jsonl.gz, raw/ trace archives) |
| Scripts | `pipeline/00_build_handwritten.py` to `08_harness_compare.py`, `lint_spec_traps.py`, `taskfiles.py` |
| Environment and grader | `environments/pycode/` (taskset.py, grader/run_pytest.py, README.md, pyproject.toml) |
| Tests | `tests/test_grader.py`, `tests/test_handwritten.py`, `tests/test_taskset_options.py`, `tests/grader_fixture/` |
| Decision log | `NOTES.md` |
