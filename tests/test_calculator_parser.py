"""DC-02 / DC-03: AST precedence/associativity, limits, malformed input."""

from __future__ import annotations

import pytest
from decimal import ROUND_UP, Decimal
from temporalio.exceptions import ApplicationError

from calculator.contracts import MAX_BINARY_OPERATORS_IN_EXPRESSION
from calculator.expression_parse import evaluate_ast_decimal, parse_calculator_expression
from calculator.limits import strip_ignorable_whitespace


def test_precedence_and_left_associative_power_parent_spec_example() -> None:
    stripped = strip_ignorable_whitespace("1 + 5^3 * (2 - 5)")
    ast = parse_calculator_expression(stripped)
    got = evaluate_ast_decimal(ast)
    assert got == Decimal("-374")


def test_final_quantize_round_up_two_dp_only_at_workflow_boundary() -> None:
    """Spec: ROUND_UP only on final workflow result; here we mirror that on the evaluated Decimal."""
    stripped = strip_ignorable_whitespace("1 + 5^3 * (2 - 5)")
    ast = parse_calculator_expression(stripped)
    raw = evaluate_ast_decimal(ast)
    final = raw.quantize(Decimal("0.01"), rounding=ROUND_UP)
    assert final == Decimal("-374.00")


def test_power_is_left_associative() -> None:
    ast = parse_calculator_expression("2^3^2")
    assert evaluate_ast_decimal(ast) == Decimal("64")


def test_binary_operator_cap_non_retryable() -> None:
    over = MAX_BINARY_OPERATORS_IN_EXPRESSION + 1
    expr = "1" + "+1" * over
    assert expr.count("+") == over
    with pytest.raises(ApplicationError) as exc:
        parse_calculator_expression(expr)
    assert exc.value.non_retryable
    assert str(MAX_BINARY_OPERATORS_IN_EXPRESSION) in exc.value.message


def test_malformed_unbalanced_open_paren() -> None:
    with pytest.raises(ApplicationError) as exc:
        parse_calculator_expression("(1+2")
    assert exc.value.non_retryable
    assert "parenthes" in exc.value.message.lower()


def test_malformed_unexpected_binary_after_operator() -> None:
    with pytest.raises(ApplicationError) as exc:
        parse_calculator_expression("1+*2")
    assert exc.value.non_retryable


def test_malformed_trailing_garbage() -> None:
    with pytest.raises(ApplicationError) as exc:
        parse_calculator_expression("1+2)")
    assert exc.value.non_retryable


def test_empty_expression() -> None:
    with pytest.raises(ApplicationError) as exc:
        parse_calculator_expression("")
    assert exc.value.non_retryable


def test_non_integral_exponent_fails() -> None:
    with pytest.raises(ApplicationError) as exc:
        evaluate_ast_decimal(parse_calculator_expression("2^0.5"))
    assert exc.value.non_retryable
    assert "integral" in exc.value.message.lower()


def test_division_by_zero_in_local_eval() -> None:
    with pytest.raises(ApplicationError) as exc:
        evaluate_ast_decimal(parse_calculator_expression("1/0"))
    assert exc.value.non_retryable
    assert "division by zero" in exc.value.message.lower()
