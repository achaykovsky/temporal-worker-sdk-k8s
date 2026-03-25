"""Per-operator activities: ``str`` decimals on the wire (high precision), no per-activity quantize."""

from __future__ import annotations

from decimal import Decimal

from temporalio import activity


@activity.defn(name="add")
async def add_activity(a: str, b: str) -> str:
    return str(Decimal(a) + Decimal(b))


@activity.defn(name="subtract")
async def subtract_activity(a: str, b: str) -> str:
    return str(Decimal(a) - Decimal(b))


@activity.defn(name="multiply")
async def multiply_activity(a: str, b: str) -> str:
    return str(Decimal(a) * Decimal(b))


@activity.defn(name="divide")
async def divide_activity(a: str, b: str) -> str:
    left, right = Decimal(a), Decimal(b)
    if right == 0:
        from temporalio.exceptions import ApplicationError

        raise ApplicationError("division by zero", non_retryable=True)
    return str(left / right)


@activity.defn(name="power")
async def power_activity(a: str, b: str) -> str:
    return str(Decimal(a) ** Decimal(b))
