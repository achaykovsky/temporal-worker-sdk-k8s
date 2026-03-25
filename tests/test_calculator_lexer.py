"""DC-01: lexer/tokenizer — valid tokens, unknown chars, length before tokenize (via parse entry)."""

from __future__ import annotations

import pytest
from temporalio.exceptions import ApplicationError

from calculator.contracts import EXPRESSION_MAX_CHARS
from calculator.expression_parse import TokenKind, parse_calculator_expression, tokenize
from calculator.limits import strip_ignorable_whitespace


def test_tokenize_simple_binary_like_expression() -> None:
    toks = tokenize("1+2")
    assert [t.kind for t in toks] == [TokenKind.NUMBER, TokenKind.PLUS, TokenKind.NUMBER]
    assert toks[0].value == "1"
    assert toks[2].value == "2"


def test_tokenize_unary_and_power_and_parens() -> None:
    toks = tokenize("-3^2")
    assert [t.kind for t in toks] == [
        TokenKind.MINUS,
        TokenKind.NUMBER,
        TokenKind.CARET,
        TokenKind.NUMBER,
    ]


def test_tokenize_decimal_forms() -> None:
    toks = tokenize(".5*2.")
    assert toks[0].kind == TokenKind.NUMBER
    assert toks[0].value == ".5"
    assert toks[2].value == "2."


def test_tokenize_unknown_character_raises_application_error() -> None:
    with pytest.raises(ApplicationError) as exc:
        tokenize("1@2")
    assert exc.value.non_retryable
    assert "invalid character" in exc.value.message.lower()


def test_parse_entry_rejects_over_max_length_before_tokenization_semantics() -> None:
    """Length enforced in parse_calculator_expression prior to tokenize (same public entry as workflow)."""
    too_long = "1" * (EXPRESSION_MAX_CHARS + 1)
    with pytest.raises(ApplicationError) as exc:
        parse_calculator_expression(too_long)
    assert exc.value.non_retryable
    assert str(EXPRESSION_MAX_CHARS) in exc.value.message


def test_strip_then_tokenize_parent_spec_example() -> None:
    s = strip_ignorable_whitespace("1 + 5^3 * (2 - 5)")
    kinds = [t.kind for t in tokenize(s)]
    assert kinds == [
        TokenKind.NUMBER,
        TokenKind.PLUS,
        TokenKind.NUMBER,
        TokenKind.CARET,
        TokenKind.NUMBER,
        TokenKind.STAR,
        TokenKind.LPAREN,
        TokenKind.NUMBER,
        TokenKind.MINUS,
        TokenKind.NUMBER,
        TokenKind.RPAREN,
    ]
