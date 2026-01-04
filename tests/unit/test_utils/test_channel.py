from __future__ import annotations

import anyio
import pytest

from lsp_client.utils.channel import OneShotTable


@pytest.mark.asyncio
async def test_wait_until_empty_initially_set() -> None:
    table = OneShotTable()
    # Should return immediately since it's initially empty
    await table.wait_until_empty()


@pytest.mark.asyncio
async def test_wait_until_empty_with_pending_request() -> None:
    table = OneShotTable()
    rx = table.reserve("request_id")

    async def complete_request() -> None:
        await anyio.sleep(0.1)
        await table.send("request_id", "response")

    async def receive_request() -> None:
        await rx.receive()

    async with anyio.create_task_group() as tg:
        tg.start_soon(receive_request)
        tg.start_soon(complete_request)
        # wait_until_empty should block until request is completed
        await table.wait_until_empty()

    assert table.completed


@pytest.mark.asyncio
async def test_wait_until_empty_multiple_requests() -> None:
    table = OneShotTable()

    rx1 = table.reserve("id1")
    rx2 = table.reserve("id2")

    async def complete_requests() -> None:
        await anyio.sleep(0.1)
        await table.send("id1", "response1")
        await table.send("id2", "response2")

    async def receive_request1() -> None:
        await rx1.receive()

    async def receive_request2() -> None:
        await rx2.receive()

    async with anyio.create_task_group() as tg:
        tg.start_soon(receive_request1)
        tg.start_soon(receive_request2)
        tg.start_soon(complete_requests)
        await table.wait_until_empty()

    assert table.completed


@pytest.mark.asyncio
async def test_wait_until_empty_timeout() -> None:
    table = OneShotTable()
    table.reserve("request_id")

    with pytest.raises(TimeoutError):
        with anyio.fail_after(0.2):
            await table.wait_until_empty()


@pytest.mark.asyncio
async def test_completed_property() -> None:
    table = OneShotTable()
    assert table.completed

    table.reserve("id1")
    assert not table.completed

    # Test that completed is False while pending
    # The actual transition to True after send is tested implicitly
    # by other tests that verify wait_until_empty works correctly
