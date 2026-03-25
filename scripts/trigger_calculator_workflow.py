"""
Start CalculatorWorkflow with a complex expression (K8-06).

Prerequisites: Temporal frontend reachable (e.g. ``kubectl port-forward -n temporal svc/temporal 7233:7233``
binding **127.0.0.1** only unless you accept LAN exposure — see README).

Environment:
  TEMPORAL_ADDRESS  default ``127.0.0.1:7233``
  TEMPORAL_NAMESPACE default ``default``
  CALC_EXPRESSION   optional override; default exercises ``+ * / ^`` and parentheses.
"""

from __future__ import annotations

import argparse
import asyncio
import os
import sys
from datetime import timedelta
from uuid import uuid4

from temporalio.client import Client

from calculator.contracts import WORKFLOW_TASK_QUEUE
from calculator.workflow import CalculatorWorkflow

# Multiple operators, parentheses, integer exponent (MVP).
_DEFAULT_EXPRESSION = "(2+3)^(2+1)*((8/4)+1)"


async def _run(expression: str, address: str, namespace: str) -> int:
    try:
        client = await Client.connect(address, namespace=namespace)
        result = await client.execute_workflow(
            CalculatorWorkflow.run,
            expression,
            id=f"calc-{uuid4()}",
            task_queue=WORKFLOW_TASK_QUEUE,
            result_type=str,
            execution_timeout=timedelta(minutes=15),
        )
    except Exception as exc:
        print(f"workflow_failed: {exc}", file=sys.stderr)
        return 1
    print(result)
    return 0


def main() -> None:
    parser = argparse.ArgumentParser(description="Trigger CalculatorWorkflow on Temporal.")
    parser.add_argument(
        "expression",
        nargs="?",
        default=os.environ.get("CALC_EXPRESSION", _DEFAULT_EXPRESSION).strip(),
        help="Expression to evaluate (default from CALC_EXPRESSION env or built-in demo).",
    )
    parser.add_argument(
        "--address",
        default=os.environ.get("TEMPORAL_ADDRESS", "127.0.0.1:7233").strip(),
        help="Temporal frontend gRPC target.",
    )
    parser.add_argument(
        "--namespace",
        default=os.environ.get("TEMPORAL_NAMESPACE", "default").strip(),
        help="Temporal namespace.",
    )
    args = parser.parse_args()
    if not args.expression:
        print("error: empty expression", file=sys.stderr)
        raise SystemExit(1)
    raise SystemExit(asyncio.run(_run(args.expression, args.address, args.namespace)))


if __name__ == "__main__":
    main()
