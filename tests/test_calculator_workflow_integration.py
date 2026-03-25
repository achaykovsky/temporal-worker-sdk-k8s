"""
API-04 / DC-06: CalculatorWorkflow schedules activities on per-operator queues.

Marked ``integration`` — excluded from default CI (``pytest -m "not integration"``)
per specs/requirements-decisions.md (no Temporal in MVP CI gate).
"""

from __future__ import annotations

import asyncio
from uuid import uuid4

import pytest
from temporalio.testing import WorkflowEnvironment
from temporalio.worker import Worker

from calculator import activities
from calculator.contracts import (
    TASK_QUEUE_ADD,
    TASK_QUEUE_DIV,
    TASK_QUEUE_MUL,
    TASK_QUEUE_POW,
    TASK_QUEUE_SUB,
    WORKFLOW_TASK_QUEUE,
)
from calculator.workflow import CalculatorWorkflow


def _all_activity_workers(client: object) -> list[Worker]:
    return [
        Worker(
            client,
            task_queue=TASK_QUEUE_ADD,
            workflows=[],
            activities=[activities.add_activity],
        ),
        Worker(
            client,
            task_queue=TASK_QUEUE_SUB,
            workflows=[],
            activities=[activities.subtract_activity],
        ),
        Worker(
            client,
            task_queue=TASK_QUEUE_MUL,
            workflows=[],
            activities=[activities.multiply_activity],
        ),
        Worker(
            client,
            task_queue=TASK_QUEUE_DIV,
            workflows=[],
            activities=[activities.divide_activity],
        ),
        Worker(
            client,
            task_queue=TASK_QUEUE_POW,
            workflows=[],
            activities=[activities.power_activity],
        ),
    ]


@pytest.mark.integration
@pytest.mark.asyncio
async def test_workflow_plus_and_multiply_hit_correct_activity_queues() -> None:
    async with await WorkflowEnvironment.start_time_skipping() as env:
        wf_worker = Worker(
            env.client,
            task_queue=WORKFLOW_TASK_QUEUE,
            workflows=[CalculatorWorkflow],
            activities=[],
        )
        add_worker = Worker(
            env.client,
            task_queue=TASK_QUEUE_ADD,
            workflows=[],
            activities=[activities.add_activity],
        )
        mul_worker = Worker(
            env.client,
            task_queue=TASK_QUEUE_MUL,
            workflows=[],
            activities=[activities.multiply_activity],
        )

        t_wf = asyncio.create_task(wf_worker.run())
        t_add = asyncio.create_task(add_worker.run())
        t_mul = asyncio.create_task(mul_worker.run())
        await asyncio.sleep(0.3)

        try:
            plus_result = await env.client.execute_workflow(
                CalculatorWorkflow.run,
                "1+2",
                id=f"calc-{uuid4()}",
                task_queue=WORKFLOW_TASK_QUEUE,
                result_type=str,
            )
            assert plus_result == "3.00"

            mul_result = await env.client.execute_workflow(
                CalculatorWorkflow.run,
                "3*4",
                id=f"calc-{uuid4()}",
                task_queue=WORKFLOW_TASK_QUEUE,
                result_type=str,
            )
            assert mul_result == "12.00"
        finally:
            await wf_worker.shutdown()
            await add_worker.shutdown()
            await mul_worker.shutdown()
            await asyncio.gather(t_wf, t_add, t_mul, return_exceptions=True)


@pytest.mark.integration
@pytest.mark.asyncio
async def test_workflow_multi_operator_precedence_and_routing() -> None:
    """DC-05 / DC-06: one workflow uses multiple operators on distinct task queues."""
    async with await WorkflowEnvironment.start_time_skipping() as env:
        wf_worker = Worker(
            env.client,
            task_queue=WORKFLOW_TASK_QUEUE,
            workflows=[CalculatorWorkflow],
            activities=[],
        )
        op_workers = _all_activity_workers(env.client)
        tasks = [asyncio.create_task(wf_worker.run())]
        tasks += [asyncio.create_task(w.run()) for w in op_workers]
        await asyncio.sleep(0.5)

        try:
            mixed = await env.client.execute_workflow(
                CalculatorWorkflow.run,
                "1+2*3",
                id=f"calc-{uuid4()}",
                task_queue=WORKFLOW_TASK_QUEUE,
                result_type=str,
            )
            assert mixed == "7.00"

            spec_expr = await env.client.execute_workflow(
                CalculatorWorkflow.run,
                "1 + 5^3 * (2 - 5)",
                id=f"calc-{uuid4()}",
                task_queue=WORKFLOW_TASK_QUEUE,
                result_type=str,
            )
            assert spec_expr == "-374.00"
        finally:
            await wf_worker.shutdown()
            for w in op_workers:
                await w.shutdown()
            await asyncio.gather(*tasks, return_exceptions=True)
