"""Calculator Temporal workflow — dispatches binary ops to per-operator activities/queues."""

from __future__ import annotations

from datetime import timedelta
from decimal import ROUND_UP, Decimal

from temporalio import workflow
from temporalio.common import RetryPolicy

from calculator.contracts import WORKFLOW_NAME, activity_and_queue_for_binary_operator
from calculator.errors import invalid_expression_error
from calculator.expression_parse import (
    AstNode,
    BinaryNode,
    NumberNode,
    UnaryNode,
    is_integral_decimal,
    parse_calculator_expression,
)
from calculator.limits import strip_ignorable_whitespace

# MVP defaults — documented in README (requirements-decisions: Temporal timeouts).
_ACTIVITY_START_TO_CLOSE = timedelta(seconds=60)
_ACTIVITY_RETRY_POLICY = RetryPolicy(
    initial_interval=timedelta(seconds=1),
    backoff_coefficient=2.0,
    maximum_interval=timedelta(seconds=30),
    maximum_attempts=5,
)


@workflow.defn(name=WORKFLOW_NAME)
class CalculatorWorkflow:
    """
    Evaluate an arithmetic expression string (ASCII; ignorable whitespace stripped).

    Unary ``+`` / ``-`` are reduced in workflow code. Each **binary** operator is executed via
    its dedicated activity on the mapped task queue. Final quantize: **2 dp**, ``ROUND_UP`` only
    on the workflow result (``specs/requirements/requirements-decisions.md``).

    Under MVP, workflow history size and end-to-end latency scale **approximately linearly** with
    the number of binary operators (one activity per binary op).
    """

    @workflow.run
    async def run(self, expression: str) -> str:
        stripped = strip_ignorable_whitespace(expression)
        ast = parse_calculator_expression(stripped)
        raw = await self._eval_ast(ast)
        final = Decimal(raw).quantize(Decimal("0.01"), rounding=ROUND_UP)
        return format(final, "f")

    async def _eval_ast(self, node: AstNode) -> str:
        if isinstance(node, NumberNode):
            return format(node.value, "f")
        if isinstance(node, UnaryNode):
            inner = Decimal(await self._eval_ast(node.child))
            out = inner if node.op == "+" else -inner
            return format(out, "f")
        if isinstance(node, BinaryNode):
            left_s = await self._eval_ast(node.left)
            right_s = await self._eval_ast(node.right)
            if node.op == "^":
                exp = Decimal(right_s)
                if not is_integral_decimal(exp):
                    raise invalid_expression_error(
                        "exponent must be integral after evaluation (see requirements-decisions)"
                    )
            activity_name, task_queue = activity_and_queue_for_binary_operator(node.op)
            return await workflow.execute_activity(
                activity_name,
                args=[left_s, right_s],
                task_queue=task_queue,
                start_to_close_timeout=_ACTIVITY_START_TO_CLOSE,
                retry_policy=_ACTIVITY_RETRY_POLICY,
                result_type=str,
            )
        raise TypeError(f"unknown AST node: {type(node)!r}")
