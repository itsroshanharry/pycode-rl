"""Unit tests for the taskset options and the harness guard. No sandbox, no model call.

Linux only: verifiers' runtimes do not import on native Windows (`fcntl`).
"""

from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

pytestmark = pytest.mark.skipif(sys.platform == "win32", reason="verifiers needs Linux")

if sys.platform != "win32":
    import verifiers.v1 as vf

    from pycode_env.taskset import (
        PyCodeConfig,
        PyCodeEnv,
        PyCodeFileTask,
        PyCodeTask,
        PyCodeTaskset,
    )

ROOT = Path(__file__).resolve().parents[1]
ROWS = [
    json.loads(line)
    for line in (ROOT / "environments/pycode/pycode_env/data/dataset.jsonl").read_text().splitlines()
    if line.strip()
]
TRAIN_ID = next(r["id"] for r in ROWS if r["split"] == "train")
TEST_ID = next(r["id"] for r in ROWS if r["split"] == "test")


def load(**config) -> list:
    return list(PyCodeTaskset(PyCodeConfig(**config)).load())


# --- taskset.ids -------------------------------------------------------------------------

def test_no_ids_loads_the_whole_split_as_before():
    assert len(load()) == sum(r["split"] == "test" for r in ROWS)
    assert len(load(split="all")) == len(ROWS)


def test_ids_select_exactly_those_tasks():
    tasks = load(split="all", ids=[TEST_ID, TRAIN_ID])
    assert sorted(t.data.id for t in tasks) == sorted([TEST_ID, TRAIN_ID])


def test_unknown_id_raises_instead_of_running_fewer_tasks():
    with pytest.raises(ValueError, match="pc-does-not-exist"):
        load(split="all", ids=[TEST_ID, "pc-does-not-exist"])


def test_id_outside_the_chosen_split_raises():
    with pytest.raises(ValueError, match=TRAIN_ID):
        load(split="test", ids=[TRAIN_ID])


def test_harness_study_selection_loads_in_file_mode():
    sel = json.loads((ROOT / "data/reports/harness/selection.json").read_text())["tasks"]
    tasks = load(split="all", ids=sel, solution="file")
    assert sorted(t.data.id for t in tasks) == sorted(sel)
    assert all(type(t) is PyCodeFileTask for t in tasks)
    assert all(t.data.scoring.mode == "isolated" for t in tasks)


# --- harness guard in PyCodeEnv.run ------------------------------------------------------

class FakeAgent:
    """Stands in for `agents.agent`: the same `harness.config.id` path, and records runs."""

    def __init__(self, harness_id: str):
        self.harness = SimpleNamespace(config=SimpleNamespace(id=harness_id))
        self.ran: list = []

    async def run(self, task):
        self.ran.append(task)


def run_env(task, harness_id: str) -> list:
    agent = FakeAgent(harness_id)
    env = object.__new__(PyCodeEnv)  # run() reads no env state
    asyncio.run(env.run(task, SimpleNamespace(agent=agent)))
    return agent.ran


def test_guard_allows_no_tools_reply_mode():
    (task,) = load(split="all", ids=[TEST_ID])
    assert type(task) is PyCodeTask
    assert run_env(task, "null") == [task]


def test_guard_allows_tool_harness_in_file_mode():
    (task,) = load(split="all", ids=[TEST_ID], solution="file")
    assert run_env(task, "bash") == [task]


def test_guard_refuses_tool_harness_in_reply_mode_before_the_agent_runs():
    (task,) = load(split="all", ids=[TEST_ID])
    agent = FakeAgent("bash")
    env = object.__new__(PyCodeEnv)
    with pytest.raises(ValueError, match="solution file"):
        asyncio.run(env.run(task, SimpleNamespace(agent=agent)))
    assert agent.ran == []  # refused before any sandbox or model call


def test_real_agent_exposes_the_harness_id_the_guard_reads():
    # Guards against the attribute path changing in a verifiers upgrade.
    for harness_id in ("null", "bash"):
        agent = vf.Agent(vf.AgentConfig(harness={"id": harness_id}, model="test/model"))
        assert agent.harness.config.id == harness_id
