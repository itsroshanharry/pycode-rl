"""PyCode: implement a Python function from a spec; graded by a hidden pytest suite.

Design (see NOTES.md for the reasoning):
- Single turn, `null` harness by default (no tools), shared scoring. The model never
  sees the sandbox; its reply is the only input to grading.
- Hidden tests/reference/mutants are extra `TaskData` fields: kept on the evaluator,
  never put in the prompt, written into the sandbox only at grading time, and deleted
  by the grader as soon as it has read them.
- Grading runs `grader/run_pytest.py` (PEP 723, deps pre-installed during `setup`,
  before the no-egress network policy applies). It isolates the candidate in an
  unprivileged worker process; see that file's docstring for the threat model.
- Grade once in `finalize` and store it on `trace.info`; the reward and metrics read it.
- Infrastructure failures raise (never a silent 0.0), so they show up as errors rather
  than as model failures.
"""

from __future__ import annotations

import json
import re
import uuid
from collections.abc import Iterator
from importlib.resources import files

import verifiers.v1 as vf

GRADER = files("pycode_env").joinpath("grader/run_pytest.py").read_bytes()
WORKDIR = "/work"
GRADE_DIR = "/tmp/pycode-grade"
# Validation gate: the reference must pass every test and at least MIN_KILLED of the
# mutants must fail (LLM mutants are sometimes equivalent code, so not all of them).
MIN_MUTANTS = 3
MIN_KILLED = 2

INSTRUCTION = (
    "Implement the Python function specified below. Use Python 3.11 and only the "
    "standard library. Reply with the complete implementation in one ```python code block."
)

_FENCE = re.compile(r"```[^\n`]*\n(.*?)```", re.DOTALL)
_THINK = re.compile(r"<think>.*?</think>", re.DOTALL)


def extract_code(reply: str | None) -> str:
    """The last fenced code block (any language tag), else the whole reply.
    Reasoning wrapped in <think> tags is removed first."""
    text = _THINK.sub("", reply or "")
    blocks = _FENCE.findall(text)
    return (blocks[-1] if blocks else text).strip()


class PyCodeData(vf.TaskData):
    entry_point: str
    tests: str
    """Hidden pytest source. Never part of the prompt."""
    reference: str
    mutants: list[str] = []
    meta: dict = {}


class PyCodeTaskConfig(vf.TaskConfig):
    call_timeout: float = 5.0
    """Wall-clock limit for one call into the candidate, in seconds."""
    total_timeout: float = 60.0
    """Wall-clock limit for all calls into one candidate, in seconds."""


class PyCodeTask(vf.Task[PyCodeData, vf.State, PyCodeTaskConfig]):
    NEEDS_CONTAINER = True

    async def setup(self, runtime: vf.Runtime) -> None:
        res = await runtime.run(["mkdir", "-p", WORKDIR], {})
        if res.exit_code:
            raise RuntimeError(f"mkdir {WORKDIR} failed: {res.stderr[-500:]}")
        # Installs pytest for the grader now, while the sandbox still has network.
        await runtime.prepare_uv_script(GRADER)

    async def _grade(self, runtime: vf.Runtime, code: str) -> dict:
        base = f"{GRADE_DIR}/{uuid.uuid4().hex}"
        await runtime.write(f"{base}/solution.py", code.encode())
        await runtime.write(f"{base}/tests.py", self.data.tests.encode())
        res = await runtime.run_uv_script(
            GRADER,
            args=[
                f"{base}/solution.py",
                f"{base}/tests.py",
                "--call-timeout", str(self.config.call_timeout),
                "--total-timeout", str(self.config.total_timeout),
            ],
        )
        if res.exit_code != 0:
            raise RuntimeError(f"grader failed (exit {res.exit_code}): {res.stderr[-2000:]}")
        grade = json.loads(res.stdout.strip().splitlines()[-1])
        if grade.get("isolated") is False:
            # The candidate ran with the grader's privileges and could have read the
            # hidden tests: refuse to report a score rather than trust it.
            raise RuntimeError("grader could not drop privileges for the candidate")
        return grade

    async def finalize(self, trace: vf.Trace, runtime: vf.Runtime) -> None:
        code = extract_code(trace.last_reply)
        if not code:
            trace.info["grade"] = {"score": 0.0, "passed": 0, "total": 0, "no_code": True}
            return
        trace.info["grade"] = await self._grade(runtime, code)

    @vf.reward(weight=1.0)
    async def passed_all_tests(self, trace: vf.Trace) -> float:
        return float(trace.info["grade"]["score"])

    @vf.metric
    async def grading_details(self, trace: vf.Trace) -> dict[str, float]:
        g = trace.info["grade"]
        return {
            "frac_tests_passed": g["passed"] / g["total"] if g["total"] else 0.0,
            "no_code": float(bool(g.get("no_code"))),
            "load_error": float(bool(g.get("load_error"))),
            "call_timeouts": float(g.get("timeouts", 0)),
        }

    async def validate(self, runtime: vf.Runtime) -> bool:
        """Gold check for `vf-validate`: reference passes every test, and enough
        mutants fail. (`vf-validate` has already run `setup` on this runtime.)"""
        ref = await self._grade(runtime, self.data.reference)
        if ref["score"] != 1.0:
            return False
        mutants = self.data.mutants
        if len(mutants) < MIN_MUTANTS:
            return False
        killed = 0
        for m in mutants:
            killed += (await self._grade(runtime, m))["score"] == 0.0
        return killed >= MIN_KILLED


class PyCodeConfig(vf.TasksetConfig):
    split: str = "test"
    """Which rows to load: "train", "test", or "all"."""
    task: PyCodeTaskConfig = PyCodeTaskConfig()


class PyCodeTaskset(vf.Taskset[PyCodeTask, PyCodeConfig]):
    def load(self) -> Iterator[PyCodeTask]:
        raw = files("pycode_env").joinpath("data/dataset.jsonl").read_text(encoding="utf-8")
        for line in raw.splitlines():
            if not line.strip():
                continue
            r = json.loads(line)
            if self.config.split not in ("all", r["split"]):
                continue
            yield PyCodeTask(
                PyCodeData(
                    id=r["id"],
                    name=r["id"],
                    prompt=f"{INSTRUCTION}\n\n{r['prompt']}",
                    entry_point=r["entry_point"],
                    tests=r["tests"],
                    reference=r["reference"],
                    mutants=r.get("mutants", []),
                    meta=r.get("meta", {}),
                    image="python:3.11-slim",
                    workdir=WORKDIR,
                    resources=vf.TaskResources(cpu=1, memory=1, disk=5),
                    timeout=vf.TaskTimeout(setup=300, agent=600, finalize=180, scoring=60),
                    network=vf.NetworkPolicyConfig(allow=[]),  # no egress once the agent starts
                ),
                self.config.task,
            )


class PyCodeEnvConfig(vf.EnvConfig):
    # Default to the tool-less `null` harness: hosted evals cannot pin a harness, and a
    # shell-equipped harness would let the agent tamper with the shared grading sandbox.
    # (Override with --env.agent.harness.id bash only together with isolated scoring.)
    agent: vf.AgentConfig = vf.AgentConfig(harness={"id": "null"})


class PyCodeEnv(vf.Env[PyCodeEnvConfig]):
    async def run(self, task: vf.Task, agents: vf.Agents) -> None:
        await agents.agent.run(task)


__all__ = ["PyCodeEnv", "PyCodeTaskset"]
