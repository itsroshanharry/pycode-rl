# NOTES.md: decision log

Running log of doc ambiguities resolved, design decisions, and cost. Newest first.

---

## CURRENT STATUS (read this first in a new session), updated 2026-11-21

**Where we are:** the leaderboard is done (4 models, hosted, `data/reports/leaderboard/`), the null vs bash comparison is done (local, `data/reports/harness/`, REPORT F8-F9), and **0.2.2** is pushed (PRIVATE) with the final README, `taskset.ids` and the harness guard.
- **Published now:** `itsroshanharry/pycode-env` **0.2.2** (wheel sha256 `7fac02a6...`, dataset `119ed403...`, grader v3). The leaderboard ran on 0.2.0 (wave 1) and 0.2.1 (wave 2); 0.2.2 changes no grading code.
- **Wallet:** $3.19 left, so spend is about $6.81 against the $7 cap (about $0.19 of room).
- **Next steps:**
  1. User: share the DeepSeek, Gemma and gpt-oss-20b runs to the Hub leaderboard (only gpt-oss-120b is shared).
  2. Hosted bash smoke test, needs user approval: 1 task x 1 attempt, gpt-oss-120b, about $0.04. The hosted `-a '{"agent": {"harness": ...}}'` path in the README is not yet verified.
  3. REPORT leaderboard chapter; move the near-miss / first-failing-test columns into `07_leaderboard.py`.
  4. Make the environment public at the end; optional PR.
  - Not run (budget): qwen3.5-9b leaderboard row, cross-benchmark calibration.

**History below this line is the 2026-11-20 status, kept for reference.**

**Where we were (2026-11-20):** dataset frozen; leaderboard wave 1 done (0.2.0), grader v3 pushed as 0.2.1, waves 2-3 running on it.
- **Dataset:** 75 tasks (38 train / 37 test), sha256 `119ed403e4977450209a44a3c2d99e7661fd0c17611c9525b7e8f1d182fc2680`.
  - Funnel: 100 written -> 100 validated -> 81 after the difficulty filter -> 75 after contamination -> 75 after the audit.
  - Audit: all 75 reviewed (DeepSeek 31 + gpt-oss-120b 44) plus a user spot-check of 8. See the Stage 6 entry below.
- **Frozen-dataset full `vf-validate`: 75/75 valid** (gold 75/75, noop 75/75, 0 errors or timeouts). Results are in `data/reports/validate/final-validate.*`, recorded with `02c_pending.py record --dataset`. **The dataset is frozen.**
- **Published:** `itsroshanharry/pycode-env` **0.2.0** (PRIVATE, wheel sha256 `0ba5264e...`; the wheel holds the 75-row dataset `119ed403...` and the grader).
  - Hosted smoke test `nmzewnbjsxv66ytoe5xz43df` (gpt-oss-20b, 2 tasks): ran on @0.2.0; c0015 scored 1.0, c0041 scored 0.0 (89% of tests passed); no errors, no truncation.
  - Hosted `--timeout-minutes` must be >= 60 (or negative).
- **Wallet:** about $7.53 (spend about $2.47).

**Next steps, in order:**
1. ~~Full vf-validate~~ done.
2. ~~Push 0.2.0 + smoke test~~ done.
3. Leaderboard (CLAUDE.md section 5; plan in the 2026-11-20 entries):
   - all 75 tasks, -r 4, temperature 1.0, reasoning_effort low, max_tokens 16384, -c 8;
   - three waves: (1) DeepSeek + gpt-oss-20b, (2) Gemma 31B + gpt-oss-120b, (3) qwen3.5-9b;
   - check spend and truncation between waves;
   - **no pushes during the waves** (hosted runs use @latest).
4. Analysis (Wilson CIs, pass@k, pass^k, failure modes, cost; all 75 plus the test-only 37), then REPORT.md.
5. Stretch: null vs bash harness comparison. Optional PR.

**Agreed decisions (don't relitigate):**
- function-level tasks (no repo pivot);
- contamination = exact n-gram + LLM-judge rephrase check (no MinHash);
- traces ON;
- hosted evals for the leaderboard;
- Claude Code generated every task (no API generator was needed);
- the SWE-env reward-hack audit is out of scope.

**How to run things:** see CLAUDE.md section 3 (Codespace workflow), section 7 (gate order) and section 9 (hosted command).

## 2026-11-21: 0.2.2 pushed: `taskset.ids`, harness guard, final README

- **Why:** anyone should be able to run both the no-tools and the bash setups, hosted or local. Hosted runs have no
  task-selection flag (`--select.include.ids` is vf-run only), so the 20-task bash study could not be reproduced
  hosted.
- **`taskset.ids: list[str] = []`:** loads only those ids (empty = all). Any id missing from `split` raises (a typo or
  wrong split must not silently shrink the run); the 20-task study spans both splits, so it needs `split: all`.
  Local flag: `--env.taskset.ids a b c` (space-separated, per `vf-run --help`).
- **Guard in `PyCodeEnv.run`:** a harness other than `null` with `solution: reply` raises before the agent runs.
  Reply mode grades in the agent's own sandbox, so a shell could plant files that fake a pass. It reads
  `agents.agent.harness.config.id` (verifiers `agent.py`: `Agent.harness = load_harness(config.harness)`).
  `Env.run_episode` records the raise as an `EnvError` on the episode, with no trace and no score.
- **Tests:** `tests/test_taskset_options.py` (9 tests, no sandbox). Full suite in the Codespace: 47 passed.
  Real vf-run checks (gpt-oss-20b, pc-c-0001, about $0.002, local only):
  - bash + reply: 0/1 episodes ok; the EnvError carries the guard message; no sandbox started.
  - null + ids: graded normally (28/30 tests, grader 3, isolated worker).
- **README:** the final Hub README (from `drafts/README_hub_draft.md`, now superseded), with:
  - the 4-model leaderboard table;
  - the null vs bash section;
  - hosted and local commands for both setups;
  - the options table.
  The hosted bash command is unverified until the smoke test.
- **Hub:** `prime env info` says private envs cannot be installed with `prime env install` (use `prime env pull`);
  the README's install line applies once the env is public.

## 2026-11-21: Hub leaderboard format (user shared gpt-oss-120b's run from the dashboard)

- **Sharing:** only from the dashboard's Share button. The CLI cannot change an existing evaluation's visibility
  ("Visibility can only be set when creating a new evaluation", prime_cli evals.py). Local v1 runs cannot be
  uploaded as evaluations: `prime eval push` is the v0 flow; v1 local runs only upload as traces.
- **Leaderboard:** one list per environment, one row per shared evaluation, sorted by Avg Reward.
  - Columns: model, status, samples ("All examples x 4 rollouts"), reasoning effort, avg reward, published by, created.
  - Not shown: our metrics, package version, env args. The version appears only in the detail panel's run command
    (`pycode-env@0.2.1`). It is visible to the owner while the env is private.
- **Consequence:** a bash run would be an unlabelled second row for the same model, ranked against no-tools runs
  on a different task subset. Proposal: the leaderboard holds the 4 no-tools runs only; the bash comparison goes
  in README/REPORT F9.

## 2026-11-21: Bash harness variant built; probes; model choice

- **Code:**
  - `taskset.solution = "file"` uses the new subclass `PyCodeFileTask`. `PyCodeTask` is
    byte-identical to the leaderboard version; only `load()` picks the class and instruction.
  - The agent writes `/work/solution.py`.
  - Isolated scoring: that file is the only artifact, normalized to a plain file in the
    solver's `finalize`, and graded in the scoring phase of a fresh sandbox with the network
    locked. The solver-marker check refuses to grade in the agent's own box.
  - If the file is missing, the reply's last code block is graded, recorded as `reply_fallback`.
  - Not pushed to the Hub (local `vf-run` only).
- **Task sample (pre-registered, `data/reports/harness/selection.json`):** 20 random tasks
  (seed 2026) from the 53 whose difficulty-filter pass rate is <= 0.5. They are chosen from
  the filter's attempts, not the leaderboard's, to avoid regression-to-the-mean bias.
- **Probes (about $0.07):** see REPORT F8.
  - The mechanics work: fresh-sandbox grading, file delivery, fallback, no-tools regression.
  - Qwen 9B costs about $0.019 per bash attempt (12-15 turns, about 100k cached input tokens),
    about 4x gpt-oss, so a Qwen pairing would exceed the $7 cap.
  - gpt-oss models try the Codex `apply_patch` command first (harness mismatch).
- **Decision (user, 2026-11-21):** gpt-oss-120b + Nemotron 3.5 Super (both about 120B MoE, two families).
  - Nemotron probe: served, uses the tools, about $0.003 per bash attempt (cache $0.02/M), no `apply_patch`.
  - Run locally with `vf-run` (`08_harness_compare.py launch/status`).
  - **Mistake:** I chose local without telling the user that local runs leave no platform record. They wanted the
    result on the leaderboard. Memory rule added: state where results will appear in every run proposal.
- **Result (REPORT F9):**
  - gpt-oss-120b: no tools 0.45 -> bash 0.30 (paired -0.15, CI -0.31 to +0.01). 7/40 attempts claimed to have
    written /work/solution.py but never did; 26/40 tried `apply_patch` first.
  - Nemotron: 0.725 -> 0.75 (+0.025, CI -0.15 to +0.18). Truncation dominates its failures in both modes.
  - Cost $0.79 against the $0.57 estimate. Wallet $3.19, so spend $6.81 and $0.19 left under the $7 cap.
- **Analysis bug caught:** bash attempts whose final reply had no code block were labelled `no_code` even when the
  file was graded. Fixed in ingest (`has_code_block = None` for bash). Only an empty graded file counts as no code.
- **Pitfall (again):** `pgrep -f`/`pkill -f` patterns match the ssh session's own command
  line. Wait on PIDs (`wait`) or use a pattern that cannot occur in the command itself.

## 2026-11-20: Leaderboard wave 1 + grader v2 bug found and fixed (0.2.1)

- **Wave 1 on 0.2.0** (all 75 tasks x 4, temperature 1.0, reasoning low, max_tokens 16384, -c 8). Wallet $7.52 -> $6.16, so **$1.37**: model fees $1.01, the rest sandboxes. Analysis with `pipeline/07_leaderboard.py`.

  | Model | pass@1 (task-bootstrap 95% CI) | pass@4 | pass^4 | truncated | model $/task |
  |---|---|---|---|---|---|
  | DeepSeek V4.1 Flash | 0.940 (0.90-0.97) | 0.987 | 0.853 | 2.0% | 0.0119 |
  | gpt-oss-20b (filter model) | 0.380 (0.30-0.46) | 0.680 | 0.107 | 0% | 0.0015 |

  - **Paired:** DeepSeek is +0.56 (CI 0.48-0.64); it is better on 66 tasks and worse on 1.
  - **Filter retest:** gpt-oss-20b, filter r8 vs leaderboard r4 on the same 75 tasks: 0.342 vs 0.380, **Pearson r = 0.84**. The difficulty labels are stable.
  - **Hard tasks** (0/8 in the filter, solved by triage): DeepSeek 0.88, gpt-oss-20b 0.05. Hard but solvable.
  - **DeepSeek failures:** 18 of 300 (12 wrong, 6 truncated). Most of the wrong answers trip stated ASCII traps (full-width digits, dotted capital I).
  - **gpt-oss-20b failures:** mostly wrong answers that still pass 86% of tests on average. One **refusal** on a benign unit-conversion task (c0083); 07_leaderboard now classifies prose-only replies as no_code.
- **Grader v2 bug (harness, not model):**
  - **Cause:** the worker exec'd the candidate in a bare dict. Valid code that looks its module up in sys.modules (a dataclass with string annotations, get_type_hints, singledispatch) failed to load with "'NoneType' object has no attribute '__dict__'".
  - **How it was found:** checking gpt-oss-20b's load errors one by one (c0001).
  - **Fix (grader v3):** a real `types.ModuleType("solution")` registered in the worker's sys.modules.
  - **Regression test:** fixture `legit/module_introspection.py`, which fails on v2 (reproduced) and passes on v3. Grader suite 28/28 (19 cheats still score 0).
  - **Impact, measured:** 1 of 600 wave-1 attempts (gpt-oss-20b c0001), 0 of DeepSeek's, 0 in the difficulty-filter traces.
- **Decision (user, option 1):**
  - pushed **0.2.1** (grader v3, same dataset 119ed403, wheel 4721718d) before wave 2; smoke test `qlneer6pw368k6qfsavvcmxd` traces show grader 3;
  - waves 2-3 run on 0.2.1;
  - the one affected wave-1 attempt was re-graded with v3 through `pipeline/07b_regrade.py`. That script puts the stored code in as the "reference" and runs `vf-validate --only-gold` in a Prime sandbox. Result: **still fails, 0 -> 0, so no score changes**;
  - therefore every leaderboard score reflects grader v3. (Limitation: vf-validate reports only valid/invalid, not the tests passed.)
- The README draft for the final push is in `drafts/README_hub_draft.md`. The Hub README for 0.2.1 is still the 0.2.0 text.

## 2026-11-20: Stage 6 audit -- 75 tasks (38 train / 37 test)

- **DeepSeek review** (`pipeline/06_review.py`; spec + tests + reference -> well-known? ambiguity? unstated checks? reference?):
  - **$0.48**, but **44 of 76 ran out of the 12k token budget while still thinking** (finish=length, reasoning_tokens=12000, no answer).
  - My mistake: no one-call probe of this new kind of call, and results were written only at the end, so stopping early would have wasted everything.
  - Lessons, now rules:
    1. probe every new kind of call, not only new models;
    2. scripts save each result as it finishes;
    3. never place a spend guard that destroys partial results.
- **32 completed reviews:** 28 ok, 3 minor, 1 major.
  - **Fixed:**
    - c0028 (major: tests accept leading/trailing whitespace and runs of spaces that the spec did not allow; the spec now says whitespace is free-form);
    - c0029 (B == 0 past the end silently appended; now ValueError, spec + 2 tests);
    - c0085 (reference accepted non-str rows; type check).
  - Dismissed: c0079 (a non-int value is outside the stated input contract).
  - The 3 fixed tasks pass 02a, 02b (1.0 / 0.975 / 0.975) and vf-validate 3/3.
- **Well-known question for all 76:** instead of paying for another model pass, the **author (Claude Code) reviewed all 76 with web verification**. This is labelled as NOT independent in the report.
  - 10 resemblances examined. **Dropped pc-hw-008** (same input/output shape as LeetCode 1943 "Describe the Painting"; also flagged by DeepSeek).
  - Kept with notes: c0010, c0082 (LC 721), c0073 (LC 399), c0046 (LC 1834), c0085 (LC 36), c0084 (LC 1494), c0031, c0045, c0016.
  - Rule: drop if an independent judge flags the task and the flag is not a clear judge error, or if a memorized solution to the known problem would pass most tests.
  - All in `data/reports/review/decisions.json`.
- Pipeline re-run downstream (assemble -> filter input -> finalize -> decide -> split): **75 tasks, 38 train / 37 test**, dataset sha256 119ed403 (not frozen until the spot-check is done).
- **User spot-check (independent human sample):** 8 tasks picked with seed 8 in `data/reports/review/spot_check.json`: c0008, c0014, c0022, c0023, c0032, c0037, c0058, c0060. Together with the 32 independent DeepSeek audits, that makes 40.
- Spend about $2.42 total; wallet $7.58.

## 2026-11-20: Leaderboard plan finalized; split revised; REPORT.md draft started

- **Leaderboard (user decision):** 5 models, **all 76 tasks, -r 4, max_tokens 16384**, temperature 1.0, reasoning low, about $2.5:
  - DeepSeek V4.1 Flash;
  - Gemma 4 31B;
  - gpt-oss-120b;
  - gpt-oss-20b (labelled filter/calibration row);
  - **qwen/qwen3.5-9b** (small tier; probe: 1.8-4.8k tokens, 0 truncated, 0/4 passes with partial credit 9-19 of 20-22 tests).
- **Qwen3.6 dropped** (cost and truncation); the finding is in REPORT.md F2.
- **Why all 76 and not only test:** this project only evaluates. More tasks give tighter CIs (about ±11 vs ±16 points); test-only scores, which come free from the same runs, are the robustness check.
- **Split revised:** only the 6 tasks changed after seeing model results are forced to train (c0004, c0035, c0036, c0037, c0061, c0078). Being run in a pilot is not tuning. Test now has 5 v3 tasks. New dataset sha256 2fecc250 (not frozen until after the audit).
- **REPORT.md draft** started with the funnel table and findings F1-F7.
- **Order from here:**
  1. stage 6 audit (model-assisted plus a user spot-check);
  2. fixes;
  3. full vf-validate on the final dataset;
  4. freeze the hash and push 0.2.0;
  5. hosted leaderboard;
  6. bash comparison.

## 2026-11-20: Stage 4 contamination + Stage 5 split -- 76 tasks, 38 train / 38 test

- **Corpora** (`pipeline/04_contamination.py fetch`, run in the Codespace; `data/external/` is git-ignored, revisions in `data/reports/contamination/sources.json`):
  - HumanEval 164 (openai/human-eval @ b9453e8);
  - MBPP 974 (google-research @ f82046b), both the authors' JSONL. `uv` could not reach PyPI from the Codespace for pyarrow, so the parquet copies were avoided;
  - LiveCodeBench code_generation_lite all 6 releases, 1055 problems (HF @ 0fe84c3, 4.5 GB streamed, problem text only).
  - Total 2193.
- **(a) Lexical, all 81 x 2193 pairs:** max 5-gram Jaccard prompt **0.011**, code **0.073** (threshold 0.5); **no shared 13-gram at all** (longest common run 0). Clean.
- **(b) LLM judge** (gpt-oss-20b, temperature 0, task + top-3 similar benchmark problems; about $0.035): **0 "same problem reworded"**; **6 "well-known problem" flags**, reviewed by hand:
  - dropped:
    - pc-hw-004 lru_trace (= LeetCode 146 semantics; my own hand-written task);
    - pc-hw-006 min_bracket_insertions (classic interval-DP "Brackets"; the judge cited the wrong LeetCode number);
    - pc-c-0026 assign_rooms (Meeting Rooms pattern);
    - pc-c-0057 point_in_polygon (standard problem; the judge was not clearly wrong);
    - pc-c-0059 checkouts (actually Project Euler **109** Darts; the judge said 170).
  - overruled: **pc-c-0040** utc_order (the judge invented "Sort the Timestamps (LeetCode)"; RFC 3339 is a real-world rule). Policy: overrule only clear judge errors.
  - REPORT point: the judge's citations were often wrong (2 wrong problem numbers, 1 invented) even when its yes/no was right, so judge reasons need human review.
- **Split** (`pipeline/05_split_export.py`, seed 2026): **76 tasks -> 38 train / 38 test.**
  - 26 "seen" tasks (pilot set, b09/v3 check, c0004, c0036) forced to train; the unseen pool stratified by band and prompt version.
  - Test bands: hard 11, high 10, low 9, mid 8. Train bands: hard 12, high 8, low 8, mid 10.
  - **Limitation:** the test split has **no v3 tasks** (all 10 v3 tasks were pilot-checked, so they are in train).
  - `dataset.jsonl` sha256 **b5159e5f16ad4d88cc46e7f802a5d206064f70c83826392a44a8e872d0623be0**, written to data/ and the package (not pushed yet).
- **Funnel so far:** 100 (90 generated + 10 hand-written) -> 81 after the difficulty filter -> 76 after contamination -> 38/38.
- Spend about $1.94; wallet $8.06.
- **Next:** stage 6 audit (40 tasks; must not be self-graded), full vf-validate on the final dataset, push 0.2.0, then the leaderboard at a 16k cap.

## 2026-11-20: Stage 3 difficulty filter done -- 81 tasks kept

- **Filter:** gpt-oss-20b, 100 tasks (10 hand-written + 90 candidates) x 8, temperature 1.0, reasoning low, 8192 cap; 800/800 ok, **0% truncated**, about $0.37. Histogram of pass counts 0..8: 25, 9, 7, 6, 7, 7, 12, 8, 19.
- **Triage of the 25 tasks at 0/8** (stronger model, `deepseek/deepseek-v4.1-flash-1017`, 1 attempt each):
  - 17 solved;
  - 6 truncated at 8192, then all 6 solved at 16384 (5.5k-13.6k tokens): genuinely long-thinking tasks;
  - 2 failed:
    - **c0004:** a spec presentation defect. Its docstring example contained a triple double quote, so any solution that copies the docstring fails to parse (DeepSeek 0/31; gpt-oss 6/8 load errors). Fixed the example and added a lint rule. (The same thing then broke the Python string used to write this note.) Re-filtered: gpt-oss 2/8, now in the keep band.
    - **c0036:** every model fails only the stated "export + SPACE (not tab)" rule. Spec checked: it is explicit, so it is kept as `hard_manual` and flagged for the audit.
- **Result (`data/filtered.jsonl`, `data/reports/difficulty_final.json`):** 57 filter band + 23 hard_triage + 1 hard_manual = **81 kept**; 19 dropped as too easy. Keep rate by version before triage: v1 14/20, v2 32/60, v3 5/10, hand-written 5/10.
- Traces kept gzipped in `data/reports/difficulty/` (1.9 MB instead of 23 MB).
- **Leaderboard implication:** 6 kept tasks need more than 8k thinking tokens even for DeepSeek, so use a **16k cap for every leaderboard model** (fair, small extra cost) instead of 8192.
- Spend so far about $1.90; wallet $8.10.

## 2026-11-20: Leaderboard line-up decided (Middle plan) + difficulty filter started

- **Budget plan "Middle"** (user decision): 5-model single-turn leaderboard + bash comparison on 2 models x 20 tasks x 2 attempts. Projected project total about $4.5-5, keeping about $5 for other projects.
- **Probes (8192 cap; Qwen at 16384):**
  - gpt-oss-120b 4/4 passed, ~1.2k tokens, 0% truncated;
  - Qwen3.6 at 16k: 1 pass, 2 genuine wrong, 1 still truncated (~12-16k tokens);
  - `poolside/laguna-s-2.1`: 404 "no longer available on the API: no provider serves";
  - substitute `qwen/qwen3-coder-next`: 404 "No allowed providers are available".
  - Both are "Gateway" models (catalog-listed but served by an outside provider). Coding-specialist slot dropped. Both failures were recorded as provider errors, not model failures (correct separation).
- **Line-up:** DeepSeek V4.1 Flash, Gemma 4 31B, gpt-oss-120b, Qwen3.6 (16k x 2 attempts), gpt-oss-20b (filter, labelled calibration row). All Hosted by Prime. CLAUDE.md section 5 updated.
- **Difficulty filter started:**
  - gpt-oss-20b on `data/filter_input.jsonl` (10 hand-written + 90 candidates) x 8 attempts, run `difficulty-r8`, launched under `nohup` in the Codespace;
  - a local watcher holds an SSH session open with a heartbeat, because the Codespace idle timeout is **10 minutes** and cannot be changed on an existing codespace (`gh api user/codespaces/<name>`);
  - summarize with `pipeline/03_difficulty.py summarize <traces>`.
- Wallet $8.62 during the filter run.

## 2026-11-20: Filter-model probes, gpt-oss-20b pilot, b09 (first v3 batch) and the v3 difficulty check

- **Probes (2 tasks x 2, 8192 tokens; about $0.02):**
  - `google/gemma-4-26b-a4b-it`: 4/4 truncated at 8192 (thinks even longer than Qwen). Ruled out.
  - `openai/gpt-oss-20b`: about 1,000 output tokens, 0 truncation, genuine wrong answers (one timed out on c0069's large test).
- **gpt-oss-20b pilot** (same 20 tasks x 4): mean 0.475, **0% truncated**, pass-count histogram 0:5, 1:4, 2:4, 3:2, 4:5, so **10/20 tasks in the mixed band** (DeepSeek 2/20, Gemma 2/20); about $0.04 for 80 rollouts (about $0.0005 each with sandbox). **Chosen as the difficulty-filter model:**
  - cheap;
  - no truncation;
  - mid-strength, so it spreads the tasks;
  - not on the leaderboard (disclose the family overlap if gpt-oss-120b is used as a baseline).
- **b09** (c0081-c0090; seeds s053, s089, s080, s060, s069, s100, s101, s077, s095, s058), written with generate_v3:
  - 3 hard: rota_hours (efficiency over a 10^12-day range), dedupe_contacts (no efficiency: argument budget), convert_quantity (no efficiency: single expression);
  - 7 medium.
  - All expected values came from independent oracles/brute force. That still caught 2 docstring examples I had hand-written (c0081 ana 86 -> 70; c0090), which shows the v3 rule is needed.
  - Gates: 02a 90/90; 02b mean 0.939, c0083 flagged at 0.725 (6 survivors in a dead table I left in the reference; plus 2 real gaps), fixed to 0.975; real gaps in c0085 (box checks below row 0 never reached by random grids) and c0090 (validation with no exams). **vf-validate 10/10.** Running tally of real gaps: **20**.
- **v3 difficulty check** (b09 10 tasks x 4, 8192 tokens; about $0.10):
  - **DeepSeek mean 0.90, unchanged from v1/v2.** 9/10 tasks 4/4. The only failure (c0083 0/4) is 4 truncations, not wrong answers.
  - gpt-oss-20b mean 0.50 (v1/v2 0.475), 5/10 tasks in the mixed band, 19 genuine wrong answers.
  - **Honest negative result:** v3's levers (more rules, stated precedence, exactness, explicit traps) did not make tasks harder for a strong reasoning model. When every rule is stated, a model that thinks for ~3k tokens follows them. Single-function, fully specified tasks appear to saturate for this tier; separation lives at mid-tier models. That is a REPORT.md finding, not a failure to hide. v3 is still kept for quality (stronger tests, explicit specs, oracle-computed values).
- `pipeline/pilot_summary.py` gained `--price-in/--price-cached/--price-out` (it had used DeepSeek prices for every model).

## 2026-11-20: 3-model pilot comparison + 4 spec defects found

Same 20 tasks x 4 (seed 2026), max_tokens 8192, temperature 1.0, reasoning_effort low. Summaries: `data/reports/pilot/`.

| | DeepSeek V4.1 Flash | Gemma 4 31B | Qwen3.6 35B A3B (stopped at 33/80) |
|---|---|---|---|
| mean reward | 0.900 | 0.650 | 0.152 |
| truncated | 7.5% | 14% | **79%** |
| mean output tokens | 3570 | 5025 | 7574 |
| token cost / rollout | ~$0.0025 | ~$0.0017 | ~$0.0077 |
| pass-count histogram (of 4) | 0:1, 1:1, 3:1, 4:17 | 0:6, 2:2, 4:12 | n/a |

- **Qwen stopped early:** the step was heading for about $1.3-1.5 (over the $1 ask-first rule) because I estimated its cost from DeepSeek's token use; it actually uses 2.5x more. Its 0.15 score is again truncation, not difficulty, so it is not viable as a filter on this budget, and the leaderboard will need a higher cap for it (cost implication). **New standing rule in CLAUDE.md: probe every new model (1-2 tasks x 2) before multi-rollout runs.** Qwen spend about $0.25-0.30.
- **Gemma is bimodal** (each task either 4/4 or 0/4) and most of its failures **miss a single test**. Inspecting them:
  - **4 spec defects (mine):** the tests rejected inputs that the spec did not exclude:
    - c0035: "digits" (full-width 0 rejected);
    - c0037: "an int" (True rejected, yet bool is an int in Python);
    - c0061: "letters" (Turkish İ rejected);
    - c0078: p "0-100" (full-width digits rejected).
    - All four specs now say ASCII, or that bool is excluded; tests unchanged.
  - New `pipeline/lint_spec_traps.py` flags tests that use non-ASCII or bool inputs while the spec never says ASCII or bool; the remaining 3 hits were reviewed as false alarms.
  - **This is the shared-error class the self-checks cannot catch; a second model found it.** REPORT.md point: spec-trap vs spec ambiguity. A trap is fair only if the spec states it.
  - Genuine Gemma failures: c0052 (a 35-digit number: precision lost, likely float/Decimal context), c0036 (escape handling; tab after export), c0069 (truncated), c0028 (2/4).
- Total pilot spend: about $0.97 across the 4 runs; wallet $8.968. No sandboxes left running.

## 2026-11-20: Pilot (20 tasks x 4, filter model) -- token cap finding + "too easy" finding

Settings: `deepseek/deepseek-v4.1-flash-1017` (live price $0.04368 in / $0.70 out per M, verified with `prime inference models`), temperature 1.0, reasoning_effort low, `-c 8`, `-s --select.seed 2026 -n 20` over `data/candidates.jsonl`. Summaries: `data/reports/pilot/*.json` (script `pipeline/pilot_summary.py`).

| | max_tokens 2048 | max_tokens 8192 |
|---|---|---|
| mean reward | 0.438 | **0.900** |
| truncated (finish_reason=length) | **56%** (45/80) | 7.5% (6/80) |
| real wrong answers | **0** | 2 |
| tasks 4/4 | 6/20 | **17/20** |
| mean output / reasoning tokens | 1705 / 1514 | 3570 / 3109 |
| wallet cost | $0.098 ($0.0012/rollout) | $0.232 ($0.0029/rollout) |

- **Finding 1 (harness, not model or task):** at 2048 tokens every failure was truncation. 38 replies were cut off during reasoning (no code); 7 were cut off mid-code (SyntaxError, because the reply had no closing fence). Using 2048 for the difficulty filter would have discarded good tasks as "unsolvable". **Decision: max_tokens 8192 for filter/leaderboard runs**, not CLAUDE.md's starting 2048. Pass rates must always be read together with the truncation rate.
- **Finding 2 (difficulty):** with enough tokens the filter model solves 17/20 tasks 4/4, so the [1/8, 7/8] keep rule would drop about 85% of candidates as too easy. Open decision: calibrate to a weaker target-policy model, make tasks harder, or both.
- Failures at 8k:
  - c0031 format_duration: 3 of 4 rollouts truncated even at 8192 (long reasoning);
  - c0036 parse_dotenv: 3 truncated plus 1 wrong ("export	A=1": the spec says "export" followed by at least one SPACE, and the model accepted a tab; a fair but subtle trap, so flag it for the audit);
  - c0052 format_number: 1 genuinely wrong answer (a "-" on a positive number).
- Spend so far: about $0.40 total; wallet $9.603.

## 2026-11-20: Incremental validation + batch b08

- **`pipeline/02c_pending.py`** (new): vf-validate only rows whose content hash is not yet in `data/reports/validated_hashes.json`.
  - Why: re-validating every candidate after each batch repeated finished work, and run time grew with every batch (b07 exceeded 10 min). Money was negligible (about $0.005-0.008 per run).
  - Row positions cannot be used (`--select.include.idx`), because the candidates file is a seeded shuffle that changes as rows are added. So it writes a separate `data/candidates_pending.jsonl`.
  - Seeded from `b07-validate` (70/70). Results files are copied into `data/reports/validate/` as evidence.
  - It caught the edited c0072 automatically, which was then re-validated alone (34 s).
  - A full vf-validate on the frozen final dataset is still required before publishing.
- **b08** (c0071-c0080; seeds s034, s042, s045, s046, s049, s059, s067, s076, s091, s102): 2 easy, 6 medium, 2 hard (convert_amount, word_diff).
  - Tasks: diff_records (type-strict equality, 1 != 1.0 != True), shipping_cost (dimensional weight, 500 g steps), convert_amount (fewest hops, lexicographic tie, exact rates, banker's rounding), allocate_orders (priority, output in input order), proration_credit, retry_delays (cap before jitter), crossword_check, percentile (numpy-style conventions, exact), group_aggregate (None sorts first, count all rows), word_diff (LCS walk, deletions win ties).
  - Gates: **02a 80/80**; **02b b08 mean 0.949, 0 flagged**; **vf-validate 10/10 + c0072 re-run**.
  - Hand-value slip: 1 (c0072, 816 g bills as 1000 g).
- **Auto-mutant survivors, b08:** **1 real gap** (c0072): with rate tables whose limits are all multiples of 500 g, the "round up to 500 g" step was invisible; even deleting it survived. Added a table with 999/1499 g limits. The rest are equivalent (e.g. c0080 base value c shifts every LCS entry by c; c0079 checks a None-ness that always coincides). Running tally of real gaps: **16**.

## 2026-11-19: Batch b07 (generate_v2)

- **b07** (c0061-c0070; seeds s027, s029, s036, s038, s039, s044, s048, s084, s096, s057): 2 easy, 7 medium, 1 hard.
  - Tasks: log_counts, parse_fixed_width (1-based columns), env_overrides (check bool before int), rollout_bucket (FNV-1a over UTF-8 bytes), income_tax (taper, round the total once), apply_discounts (exclusive groups, compounding percents), invoice_tax_diff (halves away from zero), cookies_for (RFC 6265 path-match, Max-Age delete), reconcile (efficiency), elevator_scan (SCAN, not LOOK; checked against a floor-by-floor simulation).
  - **reconcile efficiency:** reference (bisect per amount pool) 0.46 s vs `slow.py` (all pairs) about 80 s at 20k x 20k with a single amount (argument about 1.1 MB). At 15k the slow version was only about 7x the limit, so 20k was chosen.
  - Gates: assembled 70/70; **02a 70/70**; **02b b07 mean 0.919 before fixes, 0 flagged**; **vf-validate 70/70**.
  - My hand-written test values were wrong 3 more times (c0062 a 9-wide record for a 10-wide field, now built with `ljust`; c0063 `___` is a valid `_port` key; c0065 forgot the allowance floor at 0).
- **Auto-mutant survivors, b07:** **5 real gaps, fixed:**
  - c0061: CRLF line without a message;
  - c0062: a short record of only `str` fields;
  - c0065, two: both hidden by a 20% rate (fixed with rate-100 bands);
  - c0068: `Max-Age=1` must not delete.
  - The rest are equivalent (ordering constants, rounding on even numerators, already-removed start floor in c0070).
  - Running tally of real gaps: **15**.
- **Caveat for REPORT.md (shared errors):** the self-checks only catch errors where my sources DISAGREE. Reference, oracle and expected values all come from one author, so a misread rule can be wrong the same way in all three and pass every check. Coverage for that: the difficulty-filter triage (0/8 tasks are inspected; often a broken test or unclear spec) and the manual 40-task audit.

## 2026-11-19: Batch b06 (generate_v2)

- **b06** (c0051-c0060; seeds s018, s030, s017, s032, s079, s087, s074, s047, s063, s090): 2 easy, 6 medium, 2 hard (overtime_pay, checkouts).
  - Tasks: slugify (ASCII-only lowercasing; the Kelvin sign trap), format_number (locale grouping such as Indian [3, 2], banker's rounding, no "-0"), resolve_import (Python relative imports, `importlib._resolve_name` rule), deep_merge (None deletes, lists replaced, conflict policy + path message), convert_base (exact fractions, truncation), packbits (exact encoder rule; matches Apple TN1023 example), point_in_polygon (exact integer even-odd, boundary inside), overtime_pay (daily/weekly/seventh-day; max not stack), checkouts (darts; unordered earlier darts), to_e164 ("(0)" marker, 00 prefix, trunk prefix once).
  - Gates: assembled 60/60; **02a 60/60**; **02b b06 mean 0.949, 0 flagged**; **vf-validate 60/60**.
- **Expected values I computed by hand were wrong 6 times** (format_number grouping, a base-36 constant, a polygon point, 3 overtime totals). Each time the reference and an independent random-test oracle agreed, and the hand value was the outlier. For c0059 I computed counts by brute force (all ordered dart sequences, then deduplicated) instead of by hand. **Lesson for REPORT.md:** author-written expected values are a real error source, which is why every task also has an independent oracle or brute-force check.
- **Auto-mutant survivors, b06:**
  - **1 real gap**, fixed: c0055 accepted base 1 when the input was "0".
  - **The rest are equivalent.** Examples:
    - c0057 `(i - 1) % n` walks the same edges in reverse, and even-odd does not care about direction.
    - c0059 rank shifts: the treble/double/single tie-break only ever decides treble vs. single.
    - c0058 `+121` vs `+120` rounding on an always-even numerator.
  - Running tally of real gaps: **10**.

## 2026-11-19: Decisions: harness comparison stretch + naming the generation method

- **What pycode-env is today (say it accurately):** a **single-turn** executable coding environment.
  - It uses the `null` harness: the model replies once with code, never runs it, and gets no feedback.
  - Hidden tests then run in a Prime sandbox behind the isolated grader.
  - It is not a multi-turn agent environment yet. An external answer claimed it used a bash tool loop; that claim was wrong and must not go in an interview pitch.
- **Stretch goal (after the leaderboard):** the same test tasks and models under the `null` and the `bash` harness, reporting the pass-rate gain from an act -> observe -> debug loop. That is the "harness vs. model" question. Neither harness is simply better: single-turn is the clean, cheap baseline; multi-turn is more realistic but several times costlier and noisier. Changes needed for `bash`:
  1. Grade `/work/solution.py` from the sandbox instead of the last reply.
  2. Switch to **isolated scoring** (fresh sandbox, only `solution.py` copied as an artifact). With a shell, the agent could tamper with the grader script or pytest that `setup` installed in its own sandbox.
  3. Extend the cheat suite with shell-based attacks.
  4. Pilot the cost first (multi-turn = more tokens + sandbox minutes); ask before spending > $1.
- **Why isolated scoring (Pattern 1) and not single-container grading (Pattern 2) for `bash`:**
  - Today's single-turn setup is effectively a light Pattern 2: hidden tests are written only at scoring time, and the candidate runs as uid 65534. That is safe only because the `null` harness gives the model no shell.
  - Under `bash`, `setup` has already installed the grader's pytest inside the agent's own sandbox, and the agent likely runs as root there. It could edit pytest or the uv cache, plant `sitecustomize.py` (Python runs it automatically at startup), or leave a background process that rewrites files during grading.
  - A fresh grading sandbox that receives only the `solution.py` artifact (hidden tests staged via `stage_verifier`) removes all of that.
- **Full checklist (more than a config flag; one Hub package, harness chosen per run):**
  1. The solution comes from `/work/solution.py` under `bash` and from the last reply under `null`.
  2. Isolated scoring with `solution.py` as the only artifact; hidden tests and the grader enter through `stage_verifier`.
  3. New cheat tests for shell attacks (grader/pytest edits, sitecustomize, background processes, files outside /work).
  4. Test with a real `vf-run` rollout: `vf-validate` does not call `stage_verifier` in isolated mode.
  5. Push timing: hosted runs use `@latest`, so push the bash-capable version before the leaderboard starts or after it ends, never during.
  6. Cost: multi-turn context grows every turn (likely 5-10x tokens per rollout); full sandbox rate is about $0.034-0.046/hr, not $0.02. Pilot first and ask before > $1.
  7. Statistics: about 20 test tasks x 2 rollouts gives roughly ±15-20-point intervals. Use a paired design (same tasks, both harnesses) and claim only clear effects.
- **Name of the generation method:** "seed-grounded synthesis" is our own label. Closest published methods:
  - **OSS-Instruct (Magicoder, Wei et al., 2023)** grounds each generated coding problem in a real-world open-source code snippet, so problems don't collapse into textbook clones. Ours grounds each task in a short real-world *rule* (a format, protocol or business rule; `meta.seed`) instead of a code snippet.
  - **Self-Instruct (Wang et al., 2022)** bootstraps from about 175 hand-written seed tasks ("seed-based synthesis").
  - Interview phrasing: "seed-grounded synthesis, in the spirit of OSS-Instruct."

## 2026-11-19: Batch b05 (generate_v2)

- **b05** (c0041-c0050; seeds s098, s086, s009, s072, s070, s054, s037, s050, s083, s006): 2 easy (hex_color, age_parts), 6 medium, 2 hard (league_table, resolve_local).
  - Tasks: hex_color, unpack_bits, age_parts, allocate_cents, league_table (head-to-head mini-table), run_jobs (priority aging), include_order (cycle chain message, 5000-deep chains), commissions (round the running total, not each sale), freshness (Cache-Control/Expires), resolve_local (UTC from local time across offset changes).
  - Seeds skipped on purpose because their natural form is a known LeetCode problem (contamination risk): s099 text justification (LC 68), s073 rectangle union area (LC 850), s010 employee free time (LC 759).
  - **resolve_local efficiency:** reference (bisect) 0.02 s vs `slow.py` (every period per query) about 50 s for 40k queries x 20k transitions (argument about 0.93 MB). 02a: slow times out (1 timeout).
  - Gates: assembled 50/50; **02a 50/50**; **02b b05 mean 0.953, 0 flagged**; **vf-validate 50/50**.
  - **vf-validate infra fault:** a sandbox provisioning HTTP 500 hit pc-c-0027's noop check; its gold check passed in the same run. It was recorded as `error`, not `invalid` (correct: an infra fault must never count as a task failure). Re-running idx 47 alone was valid. Worth a REPORT.md line on why errors and invalid results are kept separate.
- **Authoring slips caught by `quick_selfcheck`** (my hand arithmetic in tests, not the references): c0048 had 2 wrong expected values (-1000 should be -1500; 299700100 should be 299899900).
- **c0042 authored mutant survived 02a** (2/3): the duplicate-key test only had `a` before `a!`. Added the reverse order; now 3/3.
- **Auto-mutant survivors, b05:**
  - 15 equivalent, e.g. negative inputs that still raise the same ValueError by another route, equal shifts of every team's starting stats, and rounding hiding ±1 in a redundant guard.
  - **3 real gaps, fixed:**
    - c0044: a total of -1 never took the negative branch;
    - c0045: head-to-head points must outrank head-to-head goal difference;
    - c0045: head-to-head goals scored as the final key.
    - Each now has a hand-built league test with totals equalized through an outside team.
- Running tally of real test gaps found by auto-mutants: 9 (b01-b03: 5 in c0012, c0019, c0023, c0029; b04: 1 in c0039; b05: 3 in c0044, c0045), all fixed.

## 2026-11-19: Batch b04 (generate_v2)

- **b04** (c0031-c0040; seeds s007, s008, s015, s013, s014, s024, s023, s022, s004, s002): 3 easy / 5 medium / 2 hard.
  - Tasks: format_duration, fiscal_label, normalize_uuid, check_iban, isbn_convert, parse_dotenv, toc_numbers, negotiate (HTTP Accept), cron_next, utc_order (RFC 3339).
  - `pipeline/quick_selfcheck.py` (new) runs each task's tests against its own reference on Windows. It runs author code only, never model output, and catches authoring slips before the Codespace round trip.
  - Assembled 40/40; **02a 40/40**; **02b b04 mean 0.975, 0 flagged**; **vf-validate 40/40** (gold + noop).
- **cron_next efficiency design** (worth explaining in interviews):
  - A naive minute-by-minute scan was faster than expected (8 years in 0.38 s), so a 100-year horizon would not separate it from good code.
  - Fix: make the horizon the format's own limit, **9999-12-31T23:59**, so a match that never comes means scanning until then.
    - The minute scan needs billions of steps, so `slow.py` times out on all 3 never-match tests.
    - A day-by-day scan passes: 0.66 s from year 7000.
    - The reference walks month by month (about 0.03 s).
  - The never-match tests start at years 7000 or later, on purpose. From year 0001 a day scan takes 2.2 s, too close to the 5 s limit on a slower sandbox, which would make grading flaky (sometimes pass, sometimes fail).
  - The random test never generates the impossible combination "31" with month "2", so no random call can turn into a scan to year 9999.
- **Auto-mutant survivors, b04** (10 total):
  - **9 equivalent** (the code behaves the same either way):
    - zip truncating extra weights (c0035, two of them);
    - a bad check character still raising the same ValueError (c0035);
    - the specificity rank 2->3 and two default-0->-1 changes (c0038);
    - step 0 already raising inside `range` (c0039);
    - an over-long slice (c0040);
    - an equality case that can never happen (c0031).
  - **1 real gap:** c0039 `range(1, dim + 1)` -> `dim + 2` let the code return a nonexistent date, "2024-04-31". Fixed with 3 month-end weekday tests; the survivor is now killed (0.975).
- Authoring slip: a bash heredoc broke on the quote characters in c0038's token regex, so the files were written with the Write tool instead. No data impact.

## 2026-11-18: Batch b03 (first generate_v2 batch) + grader v2 codec

- **b03** (c0021-c0030; seeds s001, s016, s020, s082, s043, s051, s056, s012, s025, s094): 1 easy / 6 medium / 3 hard. Levers recorded per task; c0026 `assign_rooms` and c0027 `rate_limit` use **efficiency** with `slow.py`.
  - Assembled 30/30; **local check 30/30**, including both `slow.py` files failing by timeout (2 timeouts each).
  - Authoring errors caught by re-derivation before any run: c0021 (2 week labels), c0022 (2 orderings). That makes 5 hand-computed expected values wrong so far out of several hundred, all caught. This argues for always pairing literal cases with an independent oracle.
- **Efficiency calibration finding:** the first measurement put c0026 at 3.18 s for its whole test file. The cost was mostly the grader codec: every int was a tagged pair `["i","123"]`, so 30k tuples were about 1.5 MB.
  - **Grader v2 codec** (`GRADER_VERSION = "2"`): None/bool/int/str travel as native JSON. Tags stay for float/bytes/list/tuple/set/frozenset/dict. Raw JSON floats and any malformed shape are rejected; exact-type checks still reject subclasses.
  - Round-trip test over all types passed; **cheat suite 27/27 as root**; local check 30/30.
- **Per-call timings** (Codespace, 2 cores; single call including the process boundary and codec):

  | Task | Reference | `slow.py` |
  |---|---|---|
  | c0026 (30k meetings) | **0.114 s** | **42.5 s** |
  | c0027 (30k requests) | **0.078 s** | **38.9 s** |

  The reference is under the 0.3 s target. `slow.py` is about 8x the 5 s limit on the faster machine, so more on the 1-vCPU sandbox. Note: the whole-file time (`reference_seconds`) includes the trusted test side's own input generation and checking, which doesn't count toward the candidate's call limit.
- **Hub package is outdated** (old grader v1, no UnicodeDecodeError fix): re-push before the next hosted run.
- **Gates on all 30 candidates:** `vf-validate` **30/30 valid** in real 1-vCPU Prime sandboxes (the 30k-element tests pass there); 0 stray sandboxes.
- **`02b` on b03:**
  - mean 0.952;
  - 1 flagged: c0022 natural_sort at 0.643 (9/14). **All 5 survivors are equivalent** (sort-tag constants 0/1 -> -1/2, and `run[-1]` vs `run[0]` on runs that are all digits or all non-digits). **Flag overridden after manual review**; the low score is an artifact of a small mutant count dominated by tag constants.
  - **2 real gaps found and closed:**
    1. c0023 `startswith('[') or endswith(']')` accepted the unclosed `"[abc"`;
    2. c0029 an invalid prefix line was ignored when the counts still matched.

    Both are now at 1.0 (31/31, 40/40).
  - Other survivors (c0024 x4, c0026 x2) are equivalent init values.
- **02b `--ids`** reruns only selected tasks and merges into the existing report (a full run on 30 tasks takes about 15 min).
- **Running total of real test gaps found by auto-mutants: 5** (b02: 3, b03: 2) that the authored mutants missed. Equivalent survivors are about 70% of all survivors.

---

## 2026-11-18: Prompt generate_v2 (difficulty levers)

- **Motivation (user):** company DSA interviews use questions that are hard to answer with AI or recall. Adopt their *principles*, not the questions: real interview questions get posted to LeetCode/GfG and are contaminated.
- **v2 levers:** twist / combo / efficiency / spec-trap (see CLAUDE.md Stage 1). Medium tasks use 1 or more, hard tasks 2 or more, recorded in `meta.levers`. If a task resembles a known problem, the twist must change the answer for tested inputs.
- **Efficiency lever closes a real gap:** b01/b02 tests check correctness mostly on small inputs, so an O(n^3) brute force would usually pass. v2 hard tasks ship `slow.py` (correct but naive). `02a` requires it to score 0 **by timing out** (`timeouts > 0`, not by being wrong) and records `reference_seconds`. `taskfiles.build_row` reads the optional `slow.py` into the row's `slow_reference` and errors if `levers` contains "efficiency" without it. Builder output for existing tasks is unchanged (candidates sha `c4408cda...`).
- **Design note:** wall-clock-based rejection is acceptable only with a large margin (reference well under 1 s vs naive above 200 s), so machine speed can't flip the result. This is consistent with the "no flaky timing assertions" rule: the test asserts outputs; the grader's time limit does the rejecting.

---

## 2026-11-18: Grader false-negative fix + batch b02

- **Grader bug found while authoring c0014 (query parsing), a false negative (correct code scored 0):**
  - The worker sends the candidate's exception as (nearest builtin class name, message), and the trusted side rebuilt it with `cls(message)`.
  - `UnicodeDecodeError` needs 5 constructor args, so the rebuild failed and it became a generic `CandidateError`.
  - A *correct* solution raising `UnicodeDecodeError` (e.g. via `bytes.decode`) would therefore fail `pytest.raises(ValueError)`.
  - **Fix:** walk the MRO to the nearest builtin ancestor constructible from a message (`UnicodeError`, still a `ValueError`).
  - **Regression test** `test_unicode_decode_error_matches_value_error` added. Grader suite now **27/27 as root**.
  - **The published Hub package (0.1.0) still has the old grader**, so re-push before the next hosted run.
- **Batch b02** (`tasks/generated/b02_claude/`, c0011-c0020; seeds s005, s026, s033, s021, s088, s078, s092, s041, s035, s052): difficulty 3 easy / 5 medium / 2 hard (labels honest rather than forced to 3/4/3; the difficulty filter measures real difficulty).
  - Skipped seeds that are famous puzzles (Roman numerals = LeetCode 13, text justification = LeetCode 68, rectangle union area = LeetCode 850).
  - Funnel: assembled 10/10; local check 10/10 (30/30 authored mutants killed). On all 20 candidates: `02b` mean mutation 0.950, 0 flagged (c0019 line coverage 0.977, branch 0.975; the uncovered line is the unreachable unknown-schema-type error); **`vf-validate` 20/20 valid**, 0 stray sandboxes.
  - **The automatic mutants found 3 real test gaps that my 3 authored mutants missed**. The other 14 b02 survivors were inspected and are equivalent (e.g. checksum `data[i-1]` instead of `data[i+1]` sums the same set of low bytes; round-robin over-long slice only beyond index n-1).
    1. c0012: deleting the "stray `$`" raise is undetected; `"$ab}"` would substitute `b`.
    2. c0012: breaking the unclosed-`${` check is undetected; `"${ab"` loops forever (tests only had a 1-char name).
    3. c0019: a list schema without `"items"` was untested; mutant `or 'items' in schema` crashes there.
  - **Fix:** tests added (`"$ab}"`, `"x$ya}z"`, `"${ab"`, `"x ${abc"`, `"${a:-x"`; list schemas without items). 02a still 20/20; 02b rerun to confirm.
  - **Process lesson for REPORT:** the authored mutants are a necessary gate, but the automatic ones are what make the "tests are strong" claim author-independent. Inspect surviving auto-mutants per task: survivors are either equivalent (fine) or a real gap (strengthen the tests).

---

## 2026-11-18: Generation pipeline + batch b01 (10 Claude-written candidates)

- `pipeline/prompts/seeds.jsonl` (written by `make_seeds.py`): **102 seeds across 11 categories** of real-world rules. No classic benchmark puzzles.
- `pipeline/prompts/generate_v1.md`: the versioned generation prompt, used verbatim by any generator.
- `pipeline/taskfiles.py`: shared task-folder -> row logic. Refactoring `00_build_handwritten.py` onto it reproduced the identical hash `ecb878e9...`.
- `01_assemble_candidates.py`: folders -> `data/candidates.jsonl`; format failures are rejected and reported, never fixed.
- `02a_local_check.py`: free grader pre-check, run in the Codespace as root.
- `taskset.dataset_path`: lets `vf-validate`/`vf-run` load a candidate file.
- **Batch b01** (`tasks/generated/b01_claude/`, generator `claude-code (claude-opus-5-5)`, prompt `generate_v1`): 10 seeds, 10 categories, difficulty 3 easy / 4 medium / 3 hard. 15-36 hidden tests each; 9/10 include a differential test against an independent oracle (for CIDR, `ipaddress.collapse_addresses`).
  - Funnel: assembled 10/10 (0 format rejects); local check 10/10 (reference passes, **30/30 mutants killed**); `vf-validate` in Prime sandboxes (gold+noop) **10/10 valid**, 0 stray sandboxes. Candidates sha256 `35b678cc0737...`.
  - Authoring note (honest): one hand-computed expected value in c0006 was wrong (13 vs 12) and was caught by re-derivation before any check ran. This is the class of error the reference-vs-literal check exists to catch.
  - **Test strength (`02b_test_strength.py`, author-independent; report `data/reports/test_strength.json`):**
    - automatic AST mutation score **mean 0.949** (range 0.829-1.0; 20-40 mutants per task);
    - **line and branch coverage 100% on all 10**;
    - the hard-coded-doctest fake **fails on all 10**;
    - **0/10 flagged.**
  - **All 17 surviving auto-mutants were inspected by hand and every one is equivalent**, so the tests kill every behaviour-changing mutant. Examples: semver internal sort tags `0/1 -> -1/2` keep the order; `>=` -> `>` on a list index still raises IndexError one step later; token-bucket `last = -1` is a no-op because the bucket starts full; CIDR `prefix > 33` still ends in ValueError via a negative shift.
  - **Lesson:** the raw mutation score understates strength by about 5 points on tasks with tag constants or redundant guards. Report it with "equivalent mutants manually verified" for a sample, not as a hard 1.0 target.

---

## 2026-11-18: Published (PRIVATE) + hosted smoke test PASSED

- **Flat layout required:** `prime env push` only detects `*.py` or `<subdir>/__init__.py` directly under the env dir (`commands/env.py:916-932`), so the `uv init --lib` **src/ layout fails** with "No environment Python file found". Moved to `environments/pycode/pycode_env/` (the prime-envs convention). Dataset hash unchanged (`ecb878e9...`). (Possible docs/CLI PR candidate.)
- Pushed `itsroshanharry/pycode-env` 0.1.0, **PRIVATE**, `--runtime v1`, wheel sha256 `f9592b92...`. Private envs can't be pip/uv-installed directly, only via `prime env pull`. `.prime/.env-metadata.json` (env id/owner/version, no secrets) is committed.
- **Hosted run 1 FAILED** (`ohm1si53...`): a TOML `taskset = {split = "train"}` becomes `env_args = {"config": {"taskset": ...}}`. The runner's prime-rl (`3bd59c1`, `src/prime_rl/entrypoints/eval.py` + `configs/orchestrator.py`) puts env_args directly into `source[0].env`, a **`vf.EnvConfig`**, which rejects `config` ("Extra inputs are not permitted").
- **Correct shape:** `-a '{"taskset": {"split": "train"}}'` on the CLI. This corrects H4: hosted runs *can* set any `vf.EnvConfig` field through `-a`, e.g. `{"agent": {...}}` and `{"taskset": {...}}`. Don't use the CLI's TOML `taskset`/`harness` sections with this runner.
- **Hosted run 2 PASSED** (`b3hl8md098kmqisdv67c7cay`), command: `prime eval run itsroshanharry/pycode-env --hosted -m deepseek/deepseek-v4.1-flash-1017 -n 2 -r 1 -c 2 -a '{"taskset": {"split": "train"}}' -S '{"reasoning_effort": "low", "max_tokens": 2048}' --timeout-minutes 120`.
  - 2/2 reward 1.0, 0% error/truncation/timeout.
  - `harness=null` (the package-default Env is honored on hosted), and the egress policy was applied.
- **Results live in Prime Traces**, not `prime eval samples` (empty for v1). `prime traces list --run-id <eval id> --output json` gives per-rollout reward, our metrics (`frac_tests_passed`, `no_code`, `load_error`, `call_timeouts`), `is_truncated`, `has_error`, `total_tokens`, `duration_ms`. About 15 KB per trace, so ingestion cost is negligible.
- **Sampling verified in the raw trace** (`prime traces get <id> --raw`): `reasoning_effort: "low"` and `max_tokens: 2048` reached the request (777 reasoning / 1142 completion tokens). **`temperature: null`**, so leaderboard and filter runs must pass `temperature` explicitly in `-S`.
- Wallet: 9.9815, so about $0.018 spent cumulatively (sandbox rows now posting).

---

## 2026-11-18: Direction decision: stay function-level (no repo pivot)

- An external review proposed pivoting to SWE-bench-style repo bug-injection. **Decision (user, 2026-11-18): keep `pycode-env` (single-function tasks) and finish it.**
- Reasons:
  - Prime already hosts about 19 SWE envs (`prime-envs/environments/swe/`), incl. `swesmith_env` (SWE-smith: 88k injected-bug tasks, about 51k Python), `r2e_gym`, `swebench_verified`/`pro`. A 50-task injected-bug set would be a small duplicate.
  - Repo rollouts cost about $0.01-0.06 each (multi-turn, no cache discount on laguna/gpt-oss, minutes of sandbox time), versus about $0.001-0.002 here.
  - The methodology (validation funnel, reward-hack hardening + control experiment, decontamination, audit, CIs) is the portfolio signal.
- Adopted from the review:
  - seed-grounded generation (`meta.seed`);
  - pass@k + **pass^k** reporting;
  - failure-mode breakdown chart;
  - 0/8 tasks get one stronger-model rollout before manual inspection;
  - the filter model may appear on the leaderboard as a disclosed baseline row;
  - the contamination judge also asks an open "is this a known LeetCode/Codeforces problem?" question.
  CLAUDE.md sections 7 and 9 are updated.
- Rejected or corrected from the review:
  - it described the v0 API (`SandboxEnv`, `load_environment`, `Rubric`, `vf-eval`);
  - it claimed "50 tasks make 10-point gaps credible" (CIs are about +/-13 points; use paired comparisons);
  - its leaderboard estimate (about $2 for 800 multi-turn rollouts) was optimistic.
- **Out of scope (separate, later project):** a reward-hack audit of Prime's existing SWE envs. Lead: `swesmith_env/taskset.py:206` notes agent edits to test files are kept as-is at scoring.

---

## 2026-11-16: Contamination plan revised (Stage 4)

- **Change:** drop MinHash-LSH and use exact all-pairs n-gram overlap (5-gram Jaccard + longest common token run) plus an **LLM-judge rephrase check** on the top-k nearest benchmark problems. CLAUDE.md Stage 4, section 3 and the layout comment are updated.
- **Why:**
  - MinHash is an *approximation* of Jaccard used for near-duplicate removal at web-corpus scale. Our scale (about 500 tasks x a few thousand benchmark problems) allows exact comparison in seconds.
  - Lab-standard benchmark decontamination is exact n-gram overlap (GPT-3: 13-gram; GPT-4: 50-char substring).
  - n-gram checks miss paraphrases. LMSYS (arXiv 2311.04850) found 8-18% rephrased HumanEval overlap in RedPajama/StarCoder-Data, and showed a model trained on rephrased test data passes n-gram decontamination. Their fix is embedding shortlist + LLM judge. Our tasks are LLM-written, so paraphrase leakage is the realistic risk.
  - We can't run embedding models locally (no heavy ML deps), so the n-gram scores provide the shortlist.
- Judge model: a cheap catalog model, ideally not one on the leaderboard. Estimate < $0.10 for about 500 tasks x top-3 candidates.
- Wallet check (2026-11-16): balance **$9.9987**. Listed billing rows total $0.0164 (sandboxes $0.0151, inference $0.0013), and only the inference amount has been deducted so far, so treat about $9.98 as available.

---

## 2026-11-16: Phase 1 built and verified (spend so far: about $0.002)

**Grader design** (`environments/pycode/pycode_env/grader/run_pytest.py`, docstring has the threat model):
- Trusted pytest runs in the grader process. The candidate runs in a separate spawned worker behind a `solution` proxy module. Calls cross as **JSON with a tagged exact-type codec** (no pickle: a malicious worker could otherwise execute code in the grader).
- As root, the worker drops to uid 65534. Also: rlimits (AS 512 MB, FSIZE 0, NPROC 32, no core dumps), fd-level `/dev/null` stdio, per-call 5 s and total 60 s timeouts, `PYTHONHASHSEED=0`.
- Input files are deleted on read; hidden tests live only in a 0700 temp dir.
- Exit 2 (raises in the task) for broken or empty test files, so a task bug is never scored as a model failure.
- **Dataset constraint this implies:** pure functions over plain data (no class entry points, no in-place mutation checks, no generators).
- The taskset **refuses a grade with `isolated: false`**, so a scoring path that could read the tests never produces a reward.

**Cheat suite** (`tests/test_grader.py`, 19 cheats + 4 legit + 3 protocol tests): **26/26 pass as root** in the Codespace.
- Cheats covered: empty, wrong name, hard-coded examples, `sys.exit` on import, `os._exit`, `raise SystemExit` / `KeyboardInterrupt`, always-equal object, int subclass with rigged `__eq__`, printing a fake result (Python and fd level), patching `_pytest` and `AssertionError`, reading the hidden tests, killing the grader, writing `conftest.py`, infinite loop (in a call and at import), memory bomb, 100 MB return value, syntax error.
- **Control experiment (REPORT finding):** without the uid drop, `read_hidden_tests` scores **8/8 (reward 1.0)** and `kill_grader` kills the grader (exit 137). The privilege drop is what defeats both.

**Hand-written tasks** (`tasks/handwritten/`, built by `pipeline/00_build_handwritten.py`; data sha256 `ecb878e9...f2a8`):
- 10 tasks across strings, parsing, DP x2, data structures, numeric, graphs, sweep line, wrapping, and binary search. Each has 10-33 hidden tests, and most include a differential check against an independently written oracle on seeded random inputs (anti-hard-coding).
- Mutants are `(desc, find, replace)` patches over the reference. **30/30 mutants killed.**
- No prompt contains a test line or a reference-body line (checked).

**Test ladder (Prime sandboxes, from the Codespace):**
- `--only-setup` -n 1: valid, 12 s.
- `--only-gold` -n 3 and `--only-noop` -n 3: 3/3 each.
- Full gold+noop on all 10: **10/10 valid**, 0 stray sandboxes.
- `vf-run -n 1 -r 1` with `deepseek/deepseek-v4.1-flash-1017`, `--sampling.reasoning_effort low --sampling.max_tokens 2048`: **reward 1.0**. `harness=null`; the egress policy allowed only the tunnel host. The grade had 14/14 tests and `isolated: true`. Usage: 290 prompt tokens, **1294 completion (884 reasoning) at effort=low**, so 2048 is close to the cap; watch truncation in the pilot. Token cost about $0.0009 per rollout.
- **Phase 1 exit criteria met:** gold/noop pass on all 10, `vf-run` returns a score, every cheat scores 0.
- Wallet 10.0000 -> 9.9987 (sandbox rows may still be posting).

---

## 2026-11-16: Project setup + Windows blocker

- Root dev project `pyproject.toml` (Python 3.12, `package = false`) pins `verifiers` to git `20c549f` (the runner's). It resolves as **0.4.1.dev150, identical to the runner**. `pycode-env` is installed editable from `environments/pycode`. `.venv` is about 300 MB; no torch.
- `environments/pycode/pyproject.toml`: `verifiers>=0.4.1.dev150`. A higher floor (e.g. prime-envs' current `>=0.4.2.dev47`) would make the runner pull a newer verifiers from PyPI. Removed the `authors` line that `uv init` filled from this machine's git identity (a work account), plus the nested `.git`.
- **BLOCKER: verifiers v1 runtimes do not import on native Windows.** `verifiers/v1/runtimes/limiters.py` and `runtimes/native_compose.py` do `import fcntl` (Unix-only), in both the runner's commit and `main`. So `vf-validate`, `vf-run`, `vf-debug`, and anything touching `vf.Runtime` fail with `ModuleNotFoundError: fcntl`. Other Unix-only bits: `os.killpg` (subprocess/docker backends) and `prctl` (MCP server). Hosted evals are unaffected (Linux). Data-only pipeline steps (generation, contamination, stats) are unaffected.
- Options: (A) run verifiers CLIs inside a Prime sandbox; (B) GitHub Codespaces (Linux, free monthly quota, VS Code attaches, no laptop RAM); (C) a local `fcntl` shim (hack, may hit more issues); (D) WSL2/Docker (excluded by CLAUDE.md).
- **Decision: (B) GitHub Codespaces.** Rule: verifiers CLIs (`vf-validate`, `vf-run`, `vf-debug`) run in the Codespace; editing, data scripts, and `prime eval run --hosted` can run on Windows.
  - Repo: private `itsroshanharry/pycode-rl`. Commits use a repo-local identity (Roshan Kumar); the laptop's global git identity belongs to someone else, so never change it. `gh` active account is `itsroshanharry` (Nikhil's accounts are still logged in, inactive). The token has no `workflow` scope, so `gh auth refresh -s workflow` is needed before pushing `.github/workflows`.
  - `.gitattributes` forces LF (global `core.autocrlf` would otherwise convert to CRLF).
  - Codespace `pycode-rl-dev-x765vwxpjwjf4p9`: 2-core `basicLinux32gb`, `--idle-timeout 10m`. Devcontainer = `mcr.microsoft.com/devcontainers/base:1-bookworm` + sshd feature. uv manages Python 3.12. (The `devcontainers/python` image's yarn apt repo has a bad GPG key, which made the sshd feature fail and dropped us into an Alpine *recovery* container: check `/workspaces/.codespaces/.persistedshare/RECOVERY-REASON-FILE`.)
  - Verified inside: Python 3.12.16, verifiers 0.4.1.dev150, `vf-validate --help` OK, Prime CLI 0.21.0, `.venv` 355 MB.
  - `PRIME_API_KEY` is a Codespaces user secret (selected repo only). It is visible in **login shells only**, so use `gh codespace ssh -c <cs> -- 'bash -lc "..."'`. `prime whoami` inside the Codespace works (`itsroshanharry`, 16-sandbox cap).

---

## 2026-11-16: Hosted probe, `primeintellect/humaneval` (eval `ndwnprmnzutjxj4wsb69l6v3`)

Command: `prime eval run primeintellect/humaneval --hosted -m deepseek/deepseek-v4.1-flash-1017 -n 2 -r 1 -c 2 -S '{"reasoning_effort":"low","max_tokens":2048}' --timeout-minutes 120 --eval-name probe-humaneval-v1 --follow`

- **Hosted v1 confirmed.** The runner banner reads "Prime Intellect Hosted Evaluation (verifiers v1 on prime-rl)". It installs **prime-rl @ `3bd59c1`** (prime-rl 0.10.0) and builds **verifiers from prime-rl's `deps/verifiers` submodule**, then runs `uv run eval '<owner>/<env>@<version>' --model ... -n ... -r ...`. It spun up one Prime sandbox per rollout ("sandbox ... up").
- **Both rollouts errored (100% error, reward 0):** `TaskError: task HumanEvalTask scoring: AttributeError: 'Runtime' object has no attribute 'prepare_execution'`. **Root cause (verified):** the Hub copy of `primeintellect/humaneval` (0.1.0, published 2026-09-13) has `taskset.py:56 await runtime.prepare_execution(VERIFY_NETWORK_ROUTES)`, an API since removed. The GitHub version was fixed on 2026-10-19 (`scoring.network`) but **never re-pushed to the Hub**. The runner's verifiers (`20c549f`) is internally consistent: it only calls `runtime.backend.prepare_execution`. *(Corrects an earlier note that blamed runner version skew.)* This is a candidate issue/PR for Prime (stretch deliverable 6).
- Runner versions: prime-rl `3bd59c1` (2026-11-03, 82 commits behind main on 2026-11-16) bundles verifiers `20c549f` (2026-11-03, 54 behind main).
- **LESSON:** hosted runs execute our package with the runner's bundled verifiers, so develop against that commit (`20c549f`) rather than `main`. This removes one source of skew; it is not proof of compatibility. The proof is a hosted `-n 1 -r 1` smoke test after every push.
- Per-rollout results: the runner logged "Prime Traces committed episodes=2" with traces on, and the dashboard has a Traces tab.
- CLI bug on Windows: `prime eval run ... --follow` crashes printing a check mark (cp1252) *after* creating the eval. Always set `PYTHONUTF8=1` / `PYTHONIOENCODING=utf-8`. Never re-run on that crash (it would create a duplicate eval).
- Cost: wallet 10.0000 -> 9.9996. Billing rows: inference $0.0004; runner sandbox $0.0084; 2 rollout sandboxes $0.0001 each. Only the inference row has been deducted so far. Re-check whether the sandbox rows get charged ("runtime not billed separately").

---

## 2026-11-16: Toolchain + login (no spend)

- uv on PATH: **0.13.8** (`Python313\Scripts\uv.exe`). A stale standalone uv 0.10.12 sits in `~\.local\bin`; it is shadowed by PATH order, so harmless.
- Prime CLI **0.21.0** via `uv tool install prime --python 3.12`, at `~\.local\bin\prime.exe`. Its help text says to pass `--plain` for agent use.
- `prime login --max-concurrent-sandboxes 16 --max-concurrent-tunnels 16`: personal account, all scopes RW except billing/factory (read-only). The API key is capped at 16 concurrent sandboxes and 16 tunnels, a guard against the `-c 128` defaults. To change it, log in again with new caps.
- Wallet: **$10.00, 0 billing rows.** 0 sandboxes running. Client `traces_opt_out = false` (left unchanged pending the H8 decision).
- **Prime username is NOT set** ("Username: Not set"). `prime env push`, and therefore hosted evals, need it. The user has to set it in the dashboard profile.

---

## 2026-11-16: Hosted evals research (no spend)

Sources: docs `tutorials-environments/hosted-evaluations.md`, `evaluating.md`, `api-reference/hosted-evaluations/create-hosted-evaluation.md`, `traces/*` (fetched 2026-11-16); Prime CLI source `_refs/prime-cli` @ `ffe0de2` (2026-11-13), mainly `commands/evals.py`, `utils/eval_config.py`, `utils/environment_runtime.py`; public Hub endpoint `GET api.primeintellect.ai/api/v1/environmentshub/<owner>/<name>/@latest`.

**Decision: hosted evals (`prime eval run <owner>/pycode-env --hosted`) are the primary path for the leaderboard.** This changes CLAUDE.md section 9's decision order.

| # | Finding | Implication |
|---|---|---|
| H1 | `prime eval run` **without `--hosted` no longer runs anything**. It prints "prime no longer runs evaluations locally" and exits. | CLAUDE.md option 2 is hosted-only. Local runs stay `vf-run` (or prime-rl `uv run eval`). |
| H2 | **v1 support: strong evidence, no explicit doc statement.** (a) `prime env push` classifies packages as `VERIFIERS_V1` when the `verifiers` lower bound is >= 0.2.0 (or with `--runtime v1`). (b) The hosted CLI folds TOML `taskset = {...}` / `harness = {...}` into `env_args.config.{taskset,harness}`, which is the v1 shape. (c) Prime Traces "supports the verifiers v1 trace format". (d) Prime's own v1 envs are public on the Hub (`primeintellect/humaneval`, `primeintellect/livecodebench`, tags `v1`, `verifiers>=0.3.1`). (e) Hosted defaults `allow_sandbox_access=true` and `allow_tunnel_access=true` match the v1 prime-runtime design (one sandbox per rollout plus a tunnel). However, the hosted docs still say `env_args` go to `load_environment()`, and the API forwards v0 flags (`--independent-scoring`, `--state-columns`). | **Probe before building on it:** a hosted run of Prime's own v1 `primeintellect/humaneval` with `-n 2 -r 1` (pennies). It also measures billing rows and trace behavior. |
| H3 | Hosted runs **always use the `@latest` published version**; the CLI resolves `/@latest` even when the local code differs. No pinning. | Freeze the package during the leaderboard (no `prime env push`). Record the Hub `version_id` and `sha256` before and after each batch. |
| H4 | **Hosted runs expose almost no v1 agent knobs.** Only `env_args` (with `config.taskset` / `config.harness`), `sampling_args`, `max_tokens`, `temperature`, `-n`, `-r`, `-c`, `--max-retries`. There is no way to set `agent.runtime`, `agent.scoring.mode`, `max_turn_tokens`, timeouts, or `select` (no shuffle or skip). | **The package must configure itself.** Make the `null` harness the default via an exported `Env` with `vf.AgentConfig(harness={"id": "null"})` instead of relying on `config.harness` being honored. Put resources, timeouts, network, and scoring on `TaskData`. Select the split through `env_args.config.taskset.split`. |
| H5 | No shuffle: `-n N` takes the **first N tasks in `load()` order**; `-n -1` means all. | Store `dataset.jsonl` in a pre-shuffled, stratified, seeded order so `-n 20` pilots are representative. Evaluate the full test split with `-n -1`. |
| H6 | CLI defaults when flags are omitted: model `openai/gpt-4.1-mini`, `-n 5`, `-r 3`. `max_concurrent` is forwarded only if given (the server may auto-compute). Timeout defaults to 1440 min (CLI docs: min 120, max 1440; API: finite 60..5256000). | Always pass `-m`, `-n`, `-r`, `-c`, and `--timeout-minutes 120`. |
| H7 | **`reasoning_effort` handling differs by input path.** A TOML `[sampling]` or `sampling_args` table moves `reasoning_effort` / `enable_thinking` into `extra_body.chat_template_kwargs` (`_normalize_sampling_args`). The CLI `-S '<json>'` path passes JSON through unchanged. | For Prime Inference models, pass `-S '{"reasoning_effort":"low","temperature":...,"max_tokens":...}'` on the CLI, from a Python driver script (PowerShell JSON quoting is fragile). Confirm in the probe that the effort reaches the model (check token counts). |
| H8 | **Traces vs results.** Hosted runs upload to Prime Traces when the *workspace* setting is on. The client opt-out (`prime config set-traces-opt-out`, `PRIME_TRACES_OPT_OUT`) controls this machine's Prime Runs routing, and opted-out runs fell back to *legacy sample storage*, **retired 2026-11-06**. With uploads off, per-rollout hosted results may not be stored anywhere. | **Revisit CLAUDE.md's "turn traces off".** At our scale traces are cheap: about 900 leaderboard traces at roughly 30 KB each is about 27 MB, about $0.03 ingestion at $1/GiB. Recommend keeping workspace uploads **on** for hosted evals with a low usage limit, and pulling per-rollout data via `prime traces list --run-id ...` / `prime traces get <id> --raw` for the CIs. Needs the user's decision. |
| H9 | Hidden tests ride in `trace.task.data`, so they are uploaded to Prime Traces (workspace-private) and ship in the Hub package. | Already in limitations (finding #12). Use `--visibility PRIVATE` until the final push. |
| H10 | Billing. With Prime Inference (no `--api-base-url`), tokens are billed at catalog rates and "the hosted evaluation sandbox runtime is not billed separately". **Unclear whether the per-rollout Prime sandboxes the v1 runtime spawns are billed.** `GET /api/v1/billing/wallet` returns the balance plus up to 100 recent billing rows. | Measure real $/rollout from billing rows after the humaneval probe and after the pilot. |
| H11 | Hosted runs execute on Prime's Linux infra, so the **Windows `prime_tunnel`/frpc risk (finding #15) does not apply to them**. It still applies to local `vf-run` pilots. `vf-validate` needs no tunnel (no model), so Stage 2 works locally either way. | Another reason to prefer hosted for model runs from this laptop. |
| H12 | Stage 3 (difficulty filter, about 300 tasks x 8 rollouts) can also run hosted, but only on the `@latest` push. Do it with a PRIVATE push whose dataset holds the validated candidates (e.g. `split="candidates"`), then push the final dataset later. | Decide when we reach Stage 3. Older Hub versions may stay downloadable. |

**Useful commands (from CLI source):** `prime eval run <slug|config.toml> --hosted [--follow]`, `prime eval list` (Type column HOSTED/LOCAL), `prime eval get <id>`, `prime eval samples <id>`, `prime eval logs <id> -f`, `prime eval stop <id>`, `prime env push [--visibility PRIVATE] [--auto-bump] [--runtime v1]`, `prime env info <slug>`.

---

## 2026-11-16: Session 1, grounding (no spend)

**State:** workspace had only CLAUDE.md. Shallow clones (read-only) in `_refs/`:
- `verifiers` @ `672d020` (2026-11-15)
- `prime-envs` @ `b41d875` (2026-11-12; envs pin `verifiers>=0.4.2.dev47`)

**Local toolchain:** git 2.51, gh, Python 3.13.5 (system), **uv 0.10.6 (pip-installed under Python313\Scripts)**, **`prime` CLI not installed**.

### Verified against source (code wins over CLAUDE.md where they differ)

| # | Topic | Finding | Action |
|---|---|---|---|
| 1 | uv version | verifiers `pyproject.toml` sets `required-version = ">=0.11.1"`; installed 0.10.6 will refuse `uv sync`. uv came from pip, so `uv self update` won't work. | Upgrade with `python -m pip install -U uv` (or switch to the standalone installer) before setup. |
| 2 | **Default harness is `bash`, not `null`** | `default_harness_id()` returns `bash` unless the taskset package exports a `Harness`. With bash + shared scoring the agent could plant `conftest.py`/`sitecustomize.py` or tamper with the grader venv. | Ship a small `Env` with `vf.AgentConfig(harness={"id": "null"})` exported in `__all__` (docs: env.md "Role defaults"), and/or always pass `--env.agent.harness.id null`. Document that `bash` requires `--env.agent.scoring.mode isolated`. |
| 3 | `vf-run` default model | `RunnerConfig.model` defaults to `deepseek/deepseek-v4-flash` (gateway, **$0.44 in / $1.32 out**, about 10x the planned filter model). | Always pass `-m` explicitly. |
| 4 | Default concurrency | `vf-run` and `vf-validate` both default `-c 128` (up to 128 live sandboxes). | Always pass `-c 8`. |
| 5 | Reasoning defaults | `deepseek/deepseek-v4.1-flash-1017` has `default_effort: "max"`, enabled by default. All 5 leaderboard models support reasoning. Reasoning tokens count against `max_tokens`, so 2048 may truncate. | Set `sampling.reasoning_effort` explicitly (supported: none/low/high/max), record it, and measure in the pilot. Consider `skip_on_truncated`. |
| 6 | `vf-validate` sandboxes | Default mode (no `--only-*`) runs gold and noop **in separate fresh runtimes**, so 2 sandboxes per task. (`building-environments.md` says "single sandbox"; `debugging.md` and the code say separate.) | Budget 2 sandboxes per candidate for full validation. 500 candidates means about 1000 sandbox boots, likely above the $0.2-0.5 estimate. Pilot first. |
| 7 | `validate()` runs after `setup()` | `vf-validate` calls `Task.setup` before `validate`. | Drop the `await self.setup(runtime)` call inside `validate()` in the CLAUDE.md sketch (redundant). |
| 8 | Hook signatures | Base is `setup(self, trace, runtime)`, but hooks are invoked by parameter name (`utils/decorators.invoke`), so `setup(self, runtime)` is valid. | Sketch signatures OK. |
| 9 | Finalize timeout | Sketch grades in `finalize` but sets no `TaskTimeout.finalize`; `scoring=120` doesn't cover it. | Add `finalize=` to `TaskTimeout`. |
| 10 | Grader deps offline | `prepare_uv_script` in `setup` caches the interpreter on the backend; `run_uv_script` reuses it with no network. Fine for shared scoring under `allow=[]`. HumanEval/LCB instead open `scoring.network` to pypi/astral. | Keep the prepare-in-setup design. If switching to isolated, `setup` re-runs in the grading sandbox, so it still works. |
| 11 | Metrics before rewards | `Task.score` runs all `@vf.metric`, then all `@vf.reward`. A reward returning a Mapping records several *summed* rewards. | Grading once in `finalize` and reading `trace.info` in both is the right shape. |
| 12 | Hidden tests in traces | `TaskData` (incl. `tests`, `reference`, `mutants`) is serialized onto `trace.task.data` in `traces.jsonl`, and `dataset.jsonl` ships in the wheel. Hidden from the agent, but **public once pushed**. | State in README/REPORT limitations (same as HumanEval). Keep traces opt-out. |
| 13 | CLI scripts | Only `vf-run`, `vf-validate`, `vf-debug` exist. No `vf-gepa`. | n/a |
| 14 | Network policy in validate | `vf-validate` never applies the execution-time egress policy (shared mode), so the no-network property is only exercised by a real `vf-run`. | Test no-egress in the anti-hack suite through `vf-run`. |
| 15 | Prime tunnel on Windows | With the prime runtime, the laptop's interception server is exposed to the sandbox via `prime_tunnel` (frpc). Nothing in v1 handles Windows specifically. | Unverified on Windows. The first `vf-run -n 1 -r 1` is the real test. |
| 16 | Heavy deps | Lockfile pulls `transformers` + `tokenizers` (via `renderers[multimodal]`) but **no torch**. `uvloop` is correctly excluded on win32. | Acceptable; note the disk usage. |
| 17 | Sandbox lifetime | `PrimeConfig.idle_timeout = 3600`s with no hard timeout. A stray sandbox lives up to 1h idle. | Still run `prime sandbox list` after every paid step. |

### Model catalog (public `GET /api/v1/models`, 2026-11-16)
All five CLAUDE.md model IDs exist, and their prices match the table exactly:
`deepseek/deepseek-v4.1-flash-1017` (hosted, 1M ctx, max out 131K), `poolside/laguna-s-2.1` (gateway, no specs listed), `qwen/qwen3.6-35b-a3b` (fp8, 262K), `google/gemma-4-31b-it` (fp4, 262K, **max out 16K**), `openai/gpt-oss-120b` (fp4, 131K).

### Reference patterns worth copying
- `prime-envs/environments/code/humaneval`: flat package layout (`packages = ["humaneval"]`), grader read via `Path(__file__).parent`, grades inside `@vf.reward(runtime)`, runs candidate in a spawned worker that never sees tests.
- `prime-envs/environments/code/livecodebench`: last-fenced-block extraction across *all* assistant messages (`extract_code`), records `pass_rate` metric + `trace.info` report, `timeout_per_test` on a `TaskConfig` subclass. Also the loader for calibration slices (`livecodebench/code_generation_lite`, release files v1-v6, official date window 8/1/2024-5/1/2025).
- `verifiers.v1.parse_pytest_outcomes(output)`: parses `pytest -rA` summary lines into `{node_id: outcome}` for the grader.
