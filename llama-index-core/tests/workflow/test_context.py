import pytest
from typing import Union, Optional

from llama_index.core.workflow.workflow import (
    Workflow,
    Context,
)
from llama_index.core.workflow.decorators import step
from llama_index.core.workflow.events import StartEvent, StopEvent
from llama_index.core.workflow.workflow import Workflow

from .conftest import OneTestEvent, AnotherTestEvent


def test_context_ctor():
    with pytest.raises(ValueError):
        ctx = Context()


@pytest.mark.asyncio()
async def test_collect_events():
    ev1 = OneTestEvent()
    ev2 = AnotherTestEvent()

    class TestWorkflow(Workflow):
        @step
        async def step1(self, _: StartEvent) -> OneTestEvent:
            return ev1

        @step
        async def step2(self, _: StartEvent) -> AnotherTestEvent:
            return ev2

        @step
        async def step3(
            self, ctx: Context, ev: Union[OneTestEvent, AnotherTestEvent]
        ) -> Optional[StopEvent]:
            events = ctx.collect_events(ev, [OneTestEvent, AnotherTestEvent])
            if events is None:
                return None
            return StopEvent(result=events)

    workflow = TestWorkflow()
    result = await workflow.run()
    assert result == [ev1, ev2]


@pytest.mark.asyncio()
async def test_set_global(session):
    c1 = Context(session=session)
    await c1.set(key="test_key", value=42)

    c2 = Context(parent=c1)
    assert await c2.get(key="test_key") == 42


@pytest.mark.asyncio()
async def test_set_private(session):
    c1 = Context(session=session)
    await c1.set(key="test_key", value=42, make_private=True)
    assert await c1.get(key="test_key") == 42

    c2 = Context(parent=c1)
    with pytest.raises(ValueError):
        await c2.get(key="test_key")


@pytest.mark.asyncio()
async def test_set_private_duplicate(session):
    c1 = Context(session=session)
    await c1.set(key="test_key", value=42)

    c2 = Context(parent=c1)
    with pytest.raises(ValueError):
        await c2.set(key="test_key", value=99, make_private=True)


@pytest.mark.asyncio()
async def test_get_default(session):
    c1 = Context(session=session)
    assert await c1.get(key="test_key", default=42) == 42


@pytest.mark.asyncio()
async def test_legacy_data(session):
    c1 = Context(session=session)
    await c1.set(key="test_key", value=42)
    assert c1.data["test_key"] == 42
