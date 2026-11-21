# PyCode-RL: report (DRAFT)

Status: draft, built up as the project runs. Every number here must be backed by a file in
`data/reports/`; the final version is written after the leaderboard.

## Planned structure
1. What the environment is (single-turn Python function tasks, hidden tests, isolated grader).
2. How the tasks were made (seed-grounded synthesis in the spirit of OSS-Instruct; prompt versions v1-v3).
3. Funnel with rejection counts at every stage.
4. Verifier design and reward-hack tests.
5. Leaderboard (Wilson 95% CIs, pass@k, pass^k, failure modes, cost per task).
6. Harness comparison (null vs bash; stretch).
7. Findings, including harness-vs-model attributions.
8. Limitations.

## Funnel (so far)
| Stage | Tasks in | Kept | Notes | Evidence |
|---|---|---|---|---|
| Generated + hand-written | - | 100 | 90 Claude-written (9 batches) + 10 hand-written | `tasks/` |
| Validation (02a/02b/vf-validate) | 100 | 100 | 20 real test gaps found by auto-mutants and fixed | `data/reports/validated_hashes.json` |
| Difficulty filter (gpt-oss-20b x 8) | 100 | 81 | 19 too easy (8/8); 25 at 0/8 triaged with DeepSeek, all kept (1 after a spec fix, 1 manual) | `data/reports/difficulty_final.json` |
| Contamination (lexical + 2 LLM judges + author web check) | 81 | 75 | lexical clean; 6 dropped as well-known problems, 1 judge flag overruled | `data/reports/contamination/decisions.json` |
| Audit (all 75: DeepSeek 31 + gpt-oss-120b 44; user spot-check 8) | 75 | 75 | 6 flagged: 1 major + 2 minor fixed, 3 dismissed (1 false positive); 1 'well-known' flag overruled with evidence | `data/reports/review/summary.json`, `decisions.json`, `spot_check.json` |
| Split | 75 | 38 train / 37 test | 6 tasks changed after seeing model results forced to train | `data/reports/split.json` |

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
