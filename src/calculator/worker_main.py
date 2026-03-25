"""
Kubernetes / container entrypoint: select workflow vs single-activity worker via ``WORKER_ROLE``.

Required env (SDK): ``TEMPORAL_ADDRESS``, ``TEMPORAL_NAMESPACE``, ``TEMPORAL_TASK_QUEUE``.
See README and ``specs/requirements/requirements-decisions.md`` (**Worker image** row).
"""

from __future__ import annotations

import os
import sys

from temporal_worker_sdk import run_worker

from calculator.activities import (
    add_activity,
    divide_activity,
    multiply_activity,
    power_activity,
    subtract_activity,
)
from calculator.workflow import CalculatorWorkflow


def main() -> None:
    role = (os.environ.get("WORKER_ROLE") or "").strip().lower()
    if role == "workflow":
        run_worker(workflows=[CalculatorWorkflow], activities=[])
        return
    if role == "add":
        run_worker(workflows=[], activities=[add_activity])
        return
    if role == "sub":
        run_worker(workflows=[], activities=[subtract_activity])
        return
    if role == "mul":
        run_worker(workflows=[], activities=[multiply_activity])
        return
    if role == "div":
        run_worker(workflows=[], activities=[divide_activity])
        return
    if role == "pow":
        run_worker(workflows=[], activities=[power_activity])
        return

    print(
        "WORKER_ROLE must be one of: workflow, add, sub, mul, div, pow "
        "(see specs/requirements/requirements-decisions.md).",
        file=sys.stderr,
    )
    sys.exit(1)


if __name__ == "__main__":
    main()
