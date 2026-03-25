"""
Temporal calculator contract — single source of truth for names, queues, and limits.

Aligned with ``specs/features/api-workflow-activity-contracts.md`` and numeric caps in
``specs/requirements/requirements-decisions.md`` (Expression input limits).
"""

from __future__ import annotations

from typing import Final

# --- Workflow (client starts here) ---

WORKFLOW_NAME: Final[str] = "CalculatorWorkflow"
WORKFLOW_TASK_QUEUE: Final[str] = "calc-workflows"

# --- Input limits (MVP locked) ---

EXPRESSION_MAX_CHARS: Final[int] = 4096
MAX_BINARY_OPERATORS_IN_EXPRESSION: Final[int] = 512

# --- Activity type names (MVP) ---

ACTIVITY_ADD: Final[str] = "add"
ACTIVITY_SUBTRACT: Final[str] = "subtract"
ACTIVITY_MULTIPLY: Final[str] = "multiply"
ACTIVITY_DIVIDE: Final[str] = "divide"
ACTIVITY_POWER: Final[str] = "power"

# --- Task queues (MVP; locked in requirements-decisions) ---

TASK_QUEUE_ADD: Final[str] = "calc-add"
TASK_QUEUE_SUB: Final[str] = "calc-sub"
TASK_QUEUE_MUL: Final[str] = "calc-mul"
TASK_QUEUE_DIV: Final[str] = "calc-div"
TASK_QUEUE_POW: Final[str] = "calc-pow"

# Normative: one binary operator → activity name + task queue (spec table).

_BINARY_OPERATOR_TO_ACTIVITY_AND_QUEUE: Final[dict[str, tuple[str, str]]] = {
    "+": (ACTIVITY_ADD, TASK_QUEUE_ADD),
    "-": (ACTIVITY_SUBTRACT, TASK_QUEUE_SUB),
    "*": (ACTIVITY_MULTIPLY, TASK_QUEUE_MUL),
    "/": (ACTIVITY_DIVIDE, TASK_QUEUE_DIV),
    "^": (ACTIVITY_POWER, TASK_QUEUE_POW),
}


def activity_and_queue_for_binary_operator(op: str) -> tuple[str, str]:
    """
    Return ``(activity_type_name, task_queue)`` for a binary operator character.

    Raises:
        KeyError: if ``op`` is not one of ``+ - * / ^``.
    """
    return _BINARY_OPERATOR_TO_ACTIVITY_AND_QUEUE[op]


def all_binary_operators() -> frozenset[str]:
    """Set of supported binary operator symbols (for tests and validation)."""
    return frozenset(_BINARY_OPERATOR_TO_ACTIVITY_AND_QUEUE.keys())
