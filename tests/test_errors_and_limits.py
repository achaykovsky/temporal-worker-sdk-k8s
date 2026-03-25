"""API-03: documented failure helpers and limit enforcement."""

from __future__ import annotations

import pytest
from temporalio.exceptions import ApplicationError

from calculator.contracts import EXPRESSION_MAX_CHARS
from calculator.errors import input_length_exceeds_limit_error, invalid_expression_error
from calculator.expression_parse import parse_calculator_expression
from calculator.limits import enforce_pre_parse_length_limit, strip_ignorable_whitespace


def test_input_length_error_is_non_retryable_and_documents_cap() -> None:
    err = input_length_exceeds_limit_error(length=EXPRESSION_MAX_CHARS + 1)
    assert isinstance(err, ApplicationError)
    assert err.non_retryable
    assert str(EXPRESSION_MAX_CHARS) in err.message
    assert "requirements-decisions" in err.message


def test_invalid_parse_raises_documented_application_error() -> None:
    stripped = strip_ignorable_whitespace("1 + * 2")
    with pytest.raises(ApplicationError) as exc:
        parse_calculator_expression(stripped)
    assert exc.value.non_retryable


def test_enforce_pre_parse_length_limit_exceeds() -> None:
    too_long = "1" * (EXPRESSION_MAX_CHARS + 1)
    with pytest.raises(ApplicationError) as exc:
        enforce_pre_parse_length_limit(too_long)
    assert exc.value.non_retryable


def test_invalid_expression_error_factory() -> None:
    err = invalid_expression_error("custom parse reason")
    assert err.non_retryable
    assert "custom parse reason" in err.message
