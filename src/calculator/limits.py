"""Expression limit checks (MVP caps from requirements-decisions)."""

from __future__ import annotations

from calculator.contracts import EXPRESSION_MAX_CHARS, MAX_BINARY_OPERATORS_IN_EXPRESSION
from calculator.errors import binary_operator_limit_exceeded_error, input_length_exceeds_limit_error


def strip_ignorable_whitespace(expression: str) -> str:
    """Remove ASCII whitespace; calculator input charset is ASCII per decisions doc."""
    return "".join(c for c in expression if not c.isspace())


def enforce_pre_parse_length_limit(stripped: str) -> None:
    """
    Fail fast if the stripped expression is longer than ``EXPRESSION_MAX_CHARS``.

    Raises:
        ApplicationError: non-retryable, with ``non_retryable=True``.
    """
    if len(stripped) > EXPRESSION_MAX_CHARS:
        raise input_length_exceeds_limit_error(length=len(stripped))


def enforce_binary_operator_budget(*, binary_operator_count: int) -> None:
    """
    Enforce max binary operators in the **parsed** expression.

    Raises:
        ApplicationError: if ``binary_operator_count`` exceeds the MVP maximum.
    """
    if binary_operator_count > MAX_BINARY_OPERATORS_IN_EXPRESSION:
        raise binary_operator_limit_exceeded_error(count=binary_operator_count)
