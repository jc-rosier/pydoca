"""Domain-Driven Design Value Object."""
from typing import Any

import pydantic


class ValueObject(pydantic.BaseModel):
    """Immutable objects with no individual identity.

    Value objects are immutable and represent a concept in the domain
    that is defined by its attributes rather than its identity. They
    have no unique identifier and are typically used to encapsulate a
    group of related attributes or properties.
    They compare equality against their attributes rather than their identities.
    """

    model_config = pydantic.ConfigDict(frozen=True, extra="forbid")

    def __init__(self, **data: Any) -> None:
        if type(self) is ValueObject:
            raise TypeError(
                "ValueObject cannot be instantiated directly. Please subclass it and define your attributes."
            )
        super().__init__(**data)
