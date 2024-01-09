"""Domain-Driven Design Aggregate Root."""
import abc

import pydantic

from .entity import Entity
from .event import Event


class AggregateRoot(Entity, abc.ABC):
    """Special type of Entity that is the root of an Aggregate of domain objects.

    Provides a clear and controlled entry point for managing and interacting with related domain objects,
    enforcing invariants, and ensuring data consistency.

    An Aggregate is a cluster of domain objects that are treated as a single unit for data changes.
    It's a way of grouping related entities and value objects together.
    Aggregates ensure that the encapsulated objects are only modified through well-defined and controlled access points.
    Aggregates help maintain the integrity of the domain model and represent consistency boundaries.

    Within an Aggregate, one specific entity is designated as the "Aggregate Root."
    The Aggregate Root is the entry point for any operations or modifications within the Aggregate.
    All external interactions, such as client code or application services,
    should go through the Aggregate Root to access or change the data within the Aggregate.
    The Aggregate Root is responsible for maintaining the integrity of the entire Aggregate by enforcing business rules and invariants.

    Attributes:
        _events: A list of domain events associated with the aggregate.
    """

    _events: list[Event] = pydantic.PrivateAttr(default_factory=list)

    def add_event(self, event: Event) -> None:
        self._events.append(event)
        return None

    def add_events(self, events: list[Event]) -> None:
        self._events.extend(events)
        return None

    def get_events(self) -> list[Event]:
        return self._events

    def clear_events(self) -> None:
        self._events.clear()
        return None
