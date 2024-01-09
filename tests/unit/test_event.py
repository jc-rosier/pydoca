import datetime

import pydantic
import pytest

import pydoca


class FakeEvent(pydoca.Event):
    attribute1: int
    attribute2: str


def test_event_immutable() -> None:
    event = FakeEvent(attribute1=10, attribute2="test")
    with pytest.raises(pydantic.ValidationError):
        event.attribute1 = 20


def test_event_equality() -> None:
    now = datetime.datetime.now(datetime.timezone.utc)
    event1 = FakeEvent(attribute1=10, attribute2="test", timestamp=now)
    event2 = FakeEvent(attribute1=10, attribute2="test", timestamp=now)
    event3 = FakeEvent(attribute1=20, attribute2="test")

    assert event1 == event2  # Same attributes, so they should be equal
    assert event1 != event3  # Different attribute value


def test_event_hash() -> None:
    now = datetime.datetime.now(datetime.timezone.utc)
    event1 = FakeEvent(attribute1=10, attribute2="test", timestamp=now)
    event2 = FakeEvent(attribute1=10, attribute2="test", timestamp=now)
    event3 = FakeEvent(attribute1=10, attribute2="test")  # Different timestamp

    assert hash(event1) == hash(
        event2
    )  # Same attributes, so their hash values should be equal
    assert hash(event1) != hash(event3)  # Different attribute value


def test_event_extra_attributes() -> None:
    with pytest.raises(pydantic.ValidationError):
        FakeEvent(attribute1=10, attribute2="test", extra_attribute=30)  # type: ignore[call-arg]


def test_direct_use_of_event() -> None:
    with pytest.raises(TypeError):
        pydoca.Event()


def test_event_timestamp_default() -> None:
    event = FakeEvent(attribute1=10, attribute2="test")
    now = datetime.datetime.now(datetime.timezone.utc)
    assert (
        event.timestamp <= now
    )  # The timestamp should be less than or equal to the current time
