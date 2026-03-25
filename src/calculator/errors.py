"""
Calculator domain failures and how they map to Temporal workflow behavior.

**Spec**: ``specs/features/api-workflow-activity-contracts.md`` (Errors) and
``specs/requirements/requirements-decisions.md`` (division by zero, parse errors,
input limits, non-retryable application failures).

Domain rules (MVP)
------------------

- **Division by zero**: fail the workflow with a **non-retryable** application error
  (activity or workflow raises :class:`temporalio.exceptions.ApplicationError` with
  ``non_retryable=True``). Do not return a numeric success.
- **Invalid parse** (malformed expression, unsupported grammar for the current workflow
  implementation): **non-retryable** application failure; message should state parse/grammar.
- **Input over limit** (character length after ignorable whitespace removal, or binary-operator
  count in the **parsed** expression over ``MAX_BINARY_OPERATORS_IN_EXPRESSION``): **non-retryable**
  application failure; fail fast on length where possible before full parse
  (see requirements-decisions).

**Infra** (activity timeout, worker unavailable): Temporal retry policy applies; workflows should
not swallow errors without logging (observability tasks).

Workflows should raise :class:`~temporalio.exceptions.ApplicationError` for domain cases so
clients see structured failure types. Use ``non_retryable=True`` for parse, limits, and domain
math errors.
"""

from __future__ import annotations

from temporalio.exceptions import ApplicationError

from calculator.contracts import EXPRESSION_MAX_CHARS, MAX_BINARY_OPERATORS_IN_EXPRESSION


def input_length_exceeds_limit_error(*, length: int) -> ApplicationError:
    """Non-retryable failure when stripped expression length exceeds the MVP cap."""
    return ApplicationError(
        (
            f"expression length ({length}) exceeds maximum ({EXPRESSION_MAX_CHARS}) "
            "characters after removing ignorable whitespace; see "
            "specs/requirements/requirements-decisions.md (Expression input limits)"
        ),
        non_retryable=True,
    )


def binary_operator_limit_exceeded_error(*, count: int) -> ApplicationError:
    """Non-retryable failure when parsed binary-operator count exceeds MVP cap."""
    return ApplicationError(
        (
            f"expression contains {count} binary operators; maximum is "
            f"{MAX_BINARY_OPERATORS_IN_EXPRESSION}; see "
            "specs/requirements/requirements-decisions.md (Expression input limits)"
        ),
        non_retryable=True,
    )


def invalid_expression_error(message: str) -> ApplicationError:
    """Non-retryable parse / grammar failure."""
    return ApplicationError(
        message,
        non_retryable=True,
    )


def division_by_zero_error() -> ApplicationError:
    """Non-retryable domain failure from divide activity or workflow guard."""
    return ApplicationError(
        "division by zero",
        non_retryable=True,
    )
