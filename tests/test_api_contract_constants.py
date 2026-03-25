"""API-01: contract constants match specs/requirements-decisions and feature API doc."""

from __future__ import annotations

from calculator.contracts import (
    ACTIVITY_ADD,
    ACTIVITY_DIVIDE,
    ACTIVITY_MULTIPLY,
    ACTIVITY_POWER,
    ACTIVITY_SUBTRACT,
    EXPRESSION_MAX_CHARS,
    MAX_BINARY_OPERATORS_IN_EXPRESSION,
    TASK_QUEUE_ADD,
    TASK_QUEUE_DIV,
    TASK_QUEUE_MUL,
    TASK_QUEUE_POW,
    TASK_QUEUE_SUB,
    WORKFLOW_NAME,
    WORKFLOW_TASK_QUEUE,
    activity_and_queue_for_binary_operator,
)


def test_workflow_name_and_queue_single_source() -> None:
    assert WORKFLOW_NAME == "CalculatorWorkflow"
    assert WORKFLOW_TASK_QUEUE == "calc-workflows"


def test_expression_limit_constants_match_decisions_doc() -> None:
    assert EXPRESSION_MAX_CHARS == 4096
    assert MAX_BINARY_OPERATORS_IN_EXPRESSION == 512


def test_activity_names_and_queues_match_api_spec_table() -> None:
    expected = {
        "+": ("add", "calc-add"),
        "-": ("subtract", "calc-sub"),
        "*": ("multiply", "calc-mul"),
        "/": ("divide", "calc-div"),
        "^": ("power", "calc-pow"),
    }
    for op, pair in expected.items():
        assert activity_and_queue_for_binary_operator(op) == pair
    assert ACTIVITY_ADD == "add"
    assert ACTIVITY_SUBTRACT == "subtract"
    assert ACTIVITY_MULTIPLY == "multiply"
    assert ACTIVITY_DIVIDE == "divide"
    assert ACTIVITY_POWER == "power"
    assert TASK_QUEUE_ADD == "calc-add"
    assert TASK_QUEUE_SUB == "calc-sub"
    assert TASK_QUEUE_MUL == "calc-mul"
    assert TASK_QUEUE_DIV == "calc-div"
    assert TASK_QUEUE_POW == "calc-pow"
