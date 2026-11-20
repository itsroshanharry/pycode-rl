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
| Contamination (lexical + LLM judge) | 81 | 76 | lexical clean; 5 dropped as well-known problems, 1 judge flag overruled | `data/reports/contamination/decisions.json` |
| Split | 76 | 38 train / 38 test | 6 tasks changed after seeing model results forced to train | `data/reports/split.json` |

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
