"""API-04 (CI-safe): parameterized routing matrix — no Temporal server required."""

from __future__ import annotations

import pytest

from calculator.contracts import activity_and_queue_for_binary_operator


@pytest.mark.parametrize(
    ("op", "activity", "queue"),
    [
        ("+", "add", "calc-add"),
        ("-", "subtract", "calc-sub"),
        ("*", "multiply", "calc-mul"),
        ("/", "divide", "calc-div"),
        ("^", "power", "calc-pow"),
    ],
)
def test_binary_operator_routes_to_contract_activity_and_queue(
    op: str,
    activity: str,
    queue: str,
) -> None:
    assert activity_and_queue_for_binary_operator(op) == (activity, queue)


def test_unknown_operator_keyerror() -> None:
    with pytest.raises(KeyError):
        activity_and_queue_for_binary_operator("%")
