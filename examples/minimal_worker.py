"""
Minimal sample worker using only the public SDK API.

Set TEMPORAL_ADDRESS, TEMPORAL_NAMESPACE, TEMPORAL_TASK_QUEUE (and optionally other vars
from the README table), then run::

    poetry run python examples/minimal_worker.py
"""

from temporal_worker_sdk import run_worker

if __name__ == "__main__":
    run_worker(workflows=[], activities=[])
