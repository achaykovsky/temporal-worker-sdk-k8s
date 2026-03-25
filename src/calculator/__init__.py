"""
Reference calculator: Temporal workflow/activity contracts and workflow implementation.

Packaged for import as ``calculator`` from ``src`` on ``PYTHONPATH`` (see README / Docker).
"""

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
from calculator.workflow import CalculatorWorkflow

__all__ = [
    "ACTIVITY_ADD",
    "ACTIVITY_DIVIDE",
    "ACTIVITY_MULTIPLY",
    "ACTIVITY_POWER",
    "ACTIVITY_SUBTRACT",
    "EXPRESSION_MAX_CHARS",
    "MAX_BINARY_OPERATORS_IN_EXPRESSION",
    "TASK_QUEUE_ADD",
    "TASK_QUEUE_DIV",
    "TASK_QUEUE_MUL",
    "TASK_QUEUE_POW",
    "TASK_QUEUE_SUB",
    "WORKFLOW_NAME",
    "WORKFLOW_TASK_QUEUE",
    "CalculatorWorkflow",
    "activity_and_queue_for_binary_operator",
]
