"""Domain-Driven Design Event."""
import datetime
from typing import Any

import pydantic

from .utils import utc_now
from .value_object import ValueObject


class Event(ValueObject):
    """Represents an event in the domain.

    Events are value objects that capture a significant occurrence or
    state change in the system. They are immutable and represent facts
    that have already happened.

    Attributes:
        timestamp: The timestamp of the event (default: utc now).
    """

    timestamp: datetime.datetime = pydantic.Field(default_factory=utc_now)

    def __init__(self, **data: Any) -> None:
        if type(self) is Event:
            raise TypeError(
                "Event cannot be instantiated directly. Please subclass it and define your attributes."
            )
        super().__init__(**data)
