"""
Full calculator expression: lexer, AST, and parser (distributed-calculator tasks DC-01–DC-03).

Precedence: ``^`` > ``* /`` > ``+ -``. ``^`` is **left-associative** at this level
(``2^3^2`` → ``(2^3)^2``). Unary ``+`` / ``-`` apply to primaries (including repeated unary).

Callers must pass **already stripped** input (no ignorable whitespace). Use
:func:`parse_calculator_expression` as the single entry that enforces length and binary-op caps.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import ROUND_CEILING, ROUND_FLOOR, Decimal, InvalidOperation
from enum import Enum, auto
from typing import Final

from calculator.errors import division_by_zero_error, invalid_expression_error
from calculator.limits import enforce_binary_operator_budget, enforce_pre_parse_length_limit


class TokenKind(Enum):
    NUMBER = auto()
    PLUS = auto()
    MINUS = auto()
    STAR = auto()
    SLASH = auto()
    CARET = auto()
    LPAREN = auto()
    RPAREN = auto()


@dataclass(frozen=True, slots=True)
class Token:
    kind: TokenKind
    value: str = ""


def is_integral_decimal(value: Decimal) -> bool:
    """True if ``value`` has no fractional part (MVP exponent rule for ``^``)."""
    lo = value.to_integral_value(rounding=ROUND_FLOOR)
    hi = value.to_integral_value(rounding=ROUND_CEILING)
    return lo == hi


_SINGLE_CHAR_KIND: Final[dict[str, TokenKind]] = {
    "+": TokenKind.PLUS,
    "-": TokenKind.MINUS,
    "*": TokenKind.STAR,
    "/": TokenKind.SLASH,
    "^": TokenKind.CARET,
    "(": TokenKind.LPAREN,
    ")": TokenKind.RPAREN,
}


def tokenize(stripped: str) -> list[Token]:
    """
    Tokenize ASCII expression (no whitespace). Unknown characters raise non-retryable error.

    Numbers: ``123``, ``123.45``, ``.5``, ``123.`` (at least one digit overall).
    """
    tokens: list[Token] = []
    n = len(stripped)
    i = 0
    while i < n:
        c = stripped[i]
        if c in _SINGLE_CHAR_KIND:
            tokens.append(Token(_SINGLE_CHAR_KIND[c]))
            i += 1
            continue
        if c.isdigit() or c == ".":
            start = i
            if c == ".":
                j = i + 1
                if j >= n or not stripped[j].isdigit():
                    raise invalid_expression_error(
                        "invalid number: '.' must be followed by a digit"
                    )
                j += 1
                while j < n and stripped[j].isdigit():
                    j += 1
                num = stripped[i:j]
                tokens.append(Token(TokenKind.NUMBER, num))
                i = j
                continue
            j = i
            while j < n and stripped[j].isdigit():
                j += 1
            if j < n and stripped[j] == ".":
                j += 1
                while j < n and stripped[j].isdigit():
                    j += 1
            num = stripped[i:j]
            tokens.append(Token(TokenKind.NUMBER, num))
            i = j
            continue
        raise invalid_expression_error(f"invalid character in expression: {c!r}")

    return tokens


@dataclass(slots=True)
class NumberNode:
    value: Decimal


@dataclass(slots=True)
class UnaryNode:
    op: str
    child: "AstNode"


@dataclass(slots=True)
class BinaryNode:
    op: str
    left: "AstNode"
    right: "AstNode"


AstNode = NumberNode | UnaryNode | BinaryNode


def count_binary_operators(node: AstNode) -> int:
    if isinstance(node, NumberNode):
        return 0
    if isinstance(node, UnaryNode):
        return count_binary_operators(node.child)
    return 1 + count_binary_operators(node.left) + count_binary_operators(node.right)


class _Parser:
    def __init__(self, tokens: list[Token]) -> None:
        self._tokens = tokens
        self._i = 0

    def _peek(self) -> Token | None:
        return self._tokens[self._i] if self._i < len(self._tokens) else None

    def _consume(self) -> Token:
        t = self._tokens[self._i]
        self._i += 1
        return t

    def parse(self) -> AstNode:
        if not self._tokens:
            raise invalid_expression_error("empty expression")
        node = self._parse_expr()
        if self._peek() is not None:
            raise invalid_expression_error("unexpected token after complete expression")
        return node

    def _parse_expr(self) -> AstNode:
        return self._parse_add_sub()

    def _parse_add_sub(self) -> AstNode:
        left = self._parse_mul_div()
        while True:
            t = self._peek()
            if t is None or t.kind not in (TokenKind.PLUS, TokenKind.MINUS):
                break
            self._consume()
            op = "+" if t.kind == TokenKind.PLUS else "-"
            right = self._parse_mul_div()
            left = BinaryNode(op, left, right)
        return left

    def _parse_mul_div(self) -> AstNode:
        left = self._parse_pow()
        while True:
            t = self._peek()
            if t is None or t.kind not in (TokenKind.STAR, TokenKind.SLASH):
                break
            self._consume()
            op = "*" if t.kind == TokenKind.STAR else "/"
            right = self._parse_pow()
            left = BinaryNode(op, left, right)
        return left

    def _parse_pow(self) -> AstNode:
        left = self._parse_unary()
        while True:
            t = self._peek()
            if t is None or t.kind != TokenKind.CARET:
                break
            self._consume()
            right = self._parse_unary()
            left = BinaryNode("^", left, right)
        return left

    def _parse_unary(self) -> AstNode:
        t = self._peek()
        if t is None:
            raise invalid_expression_error("unexpected end of expression")
        if t.kind == TokenKind.PLUS:
            self._consume()
            return UnaryNode("+", self._parse_unary())
        if t.kind == TokenKind.MINUS:
            self._consume()
            return UnaryNode("-", self._parse_unary())
        return self._parse_primary()

    def _parse_primary(self) -> AstNode:
        t = self._peek()
        if t is None:
            raise invalid_expression_error("unexpected end of expression")
        if t.kind == TokenKind.NUMBER:
            self._consume()
            try:
                d = Decimal(t.value)
            except InvalidOperation as exc:
                raise invalid_expression_error(f"invalid numeric literal: {t.value!r}") from exc
            return NumberNode(d)
        if t.kind == TokenKind.LPAREN:
            self._consume()
            inner = self._parse_expr()
            closing = self._peek()
            if closing is None or closing.kind != TokenKind.RPAREN:
                raise invalid_expression_error("unbalanced parentheses: expected ')'")
            self._consume()
            return inner
        raise invalid_expression_error("expected number or '('")


def parse_tokens(tokens: list[Token]) -> AstNode:
    return _Parser(tokens).parse()


def parse_calculator_expression(stripped: str) -> AstNode:
    """
    Strip must already be whitespace-free. Enforces max length **before** tokenization,
    then parses and enforces max binary operators.
    """
    enforce_pre_parse_length_limit(stripped)
    if not stripped:
        raise invalid_expression_error("empty expression")
    tokens = tokenize(stripped)
    ast = parse_tokens(tokens)
    enforce_binary_operator_budget(binary_operator_count=count_binary_operators(ast))
    return ast


def evaluate_ast_decimal(node: AstNode) -> Decimal:
    """
    Pure Decimal evaluation (mirrors activity semantics for tests / local verification).

    Enforces integral exponent for ``^`` (MVP) and division-by-zero domain rule.
    """
    if isinstance(node, NumberNode):
        return node.value
    if isinstance(node, UnaryNode):
        v = evaluate_ast_decimal(node.child)
        return v if node.op == "+" else -v
    if isinstance(node, BinaryNode):
        left = evaluate_ast_decimal(node.left)
        right = evaluate_ast_decimal(node.right)
        if node.op == "+":
            return left + right
        if node.op == "-":
            return left - right
        if node.op == "*":
            return left * right
        if node.op == "/":
            if right == 0:
                raise division_by_zero_error()
            return left / right
        if node.op == "^":
            if not is_integral_decimal(right):
                raise invalid_expression_error(
                    "exponent must be integral after evaluation (see requirements-decisions)"
                )
            return left ** int(right)
    raise TypeError(f"unknown AST node: {type(node)!r}")
