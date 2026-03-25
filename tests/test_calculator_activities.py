"""DC-04: per-operator activities — str Decimal wire format, edge cases, divide by zero."""

from __future__ import annotations

from decimal import Decimal

import pytest
from temporalio.exceptions import ApplicationError

from calculator import activities


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("fn", "a", "b", "expected_decimal"),
    [
        (activities.add_activity, "0.1", "0.2", Decimal("0.3")),
        (activities.subtract_activity, "1.00", "2.5", Decimal("-1.5")),
        (activities.multiply_activity, "3", "4", Decimal("12")),
        (activities.power_activity, "2", "8", Decimal("256")),
    ],
)
async def test_binary_activity_decimal_str_wire(
    fn: object,
    a: str,
    b: str,
    expected_decimal: Decimal,
) -> None:
    out = await fn(a, b)  # type: ignore[misc]
    assert Decimal(out) == expected_decimal


@pytest.mark.asyncio
async def test_divide_activity_ok() -> None:
    assert await activities.divide_activity("1", "8") == "0.125"


@pytest.mark.asyncio
async def test_divide_by_zero_raises_non_retryable_application_error() -> None:
    with pytest.raises(ApplicationError) as exc:
        await activities.divide_activity("1", "0")
    assert exc.value.non_retryable
    assert "division by zero" in exc.value.message.lower()
