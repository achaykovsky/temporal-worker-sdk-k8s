"""
Minimal sample worker using only the public SDK API.

Set TEMPORAL_ADDRESS, TEMPORAL_NAMESPACE, TEMPORAL_TASK_QUEUE (and optionally other vars
from the README table), then run::

    poetry run python examples/minimal_worker.py

Temporal requires at least one workflow or activity on the worker; this example registers
a no-op activity so the process can poll until you stop it.

After startup, the process blocks while polling the task queue. That is normal: there is
no steady stream of output until workflows schedule this activity. Stop the worker with
Ctrl+C (Windows) or SIGTERM on Unix.
"""

import sys

from temporalio import activity

from temporal_worker_sdk import run_worker


@activity.defn(name="minimal-noop")
async def minimal_noop() -> None:
    """Placeholder so the worker has a registration; replace with your real activities."""


if __name__ == "__main__":
    print(
        "minimal_worker: polling (idle until tasks). Ctrl+C to stop.",
        file=sys.stderr,
        flush=True,
    )
    run_worker(workflows=[], activities=[minimal_noop])
