"""Unit tests for calculator.worker_main role dispatch (no Temporal)."""

from __future__ import annotations

import pytest

import calculator.worker_main as worker_main
from calculator.activities import (
    add_activity,
    divide_activity,
    multiply_activity,
    power_activity,
    subtract_activity,
)
from calculator.workflow import CalculatorWorkflow


def test_main_unknown_role_exits(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("WORKER_ROLE", "not-a-role")
    with pytest.raises(SystemExit) as exc:
        worker_main.main()
    assert exc.value.code == 1


@pytest.mark.parametrize(
    ("role", "expect_workflows", "expect_activities"),
    [
        ("workflow", [CalculatorWorkflow], []),
        ("add", [], [add_activity]),
        ("sub", [], [subtract_activity]),
        ("mul", [], [multiply_activity]),
        ("div", [], [divide_activity]),
        ("pow", [], [power_activity]),
    ],
)
def test_main_dispatches_by_role(
    monkeypatch: pytest.MonkeyPatch,
    role: str,
    expect_workflows: list,
    expect_activities: list,
) -> None:
    monkeypatch.setenv("WORKER_ROLE", role)
    captured: dict[str, object] = {}

    def fake_run_worker(*, workflows, activities, **_kwargs: object) -> None:
        captured["workflows"] = list(workflows)
        captured["activities"] = list(activities)

    monkeypatch.setattr(worker_main, "run_worker", fake_run_worker)
    worker_main.main()
    assert captured["workflows"] == expect_workflows
    assert captured["activities"] == expect_activities


def test_main_normalizes_role_whitespace(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("WORKER_ROLE", "  WORKFLOW  ")
    captured: dict[str, object] = {}

    def fake_run_worker(*, workflows, activities, **_kwargs: object) -> None:
        captured["workflows"] = list(workflows)
        captured["activities"] = list(activities)

    monkeypatch.setattr(worker_main, "run_worker", fake_run_worker)
    worker_main.main()
    assert captured["workflows"] == [CalculatorWorkflow]
    assert captured["activities"] == []
