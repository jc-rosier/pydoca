"""Domain-Driven Design Entity."""
import abc
from typing import Optional, Union

import pydantic

ID = Union[bytes, float, int, str]


class Entity(pydantic.BaseModel, abc.ABC):
    """Represents the core concepts of the business being model.

    An entity is an object that is defined not by its attributes, but by its identity.

    Entities encapsulate business logic and invariants, ensuring that the data within the entity remains consistent
    and adheres to the domain's rules.
    Changes to an entity's attributes are made through defined methods, allowing for controlled updates and validation.
    They represent the nouns and primary objects that matter in the domain.

    It has a lifecycle and its identity remains constant throughout its existence.
    Entities are distinguishable from other entities based on their unique ID.

    Entities can be part of Aggregates, where they are grouped together with other entities and Value Objects
    under the control of an Aggregate Root.
    This relationship helps maintain consistency and enforces boundaries within the domain model.
    Entities have a lifecycle, they can be created, updated or deleted, but their identities remain the same.
    Entities should be persisted via the Aggregate Root only.

    Properties:
        id: The unique identifier of the entity. Result of the implementation of the abstract method `_id`.

    Methods:
        _id: Abstract method to implement that must return the entity ID.
        __eq__: Checks if two entities are equal based on their IDs.
        __hash__: Returns the hash value of the entity based on its ID.
        __str__: Returns a string representation of the entity.
    """

    @pydantic.computed_field  # type: ignore  # https://github.com/python/mypy/issues/14461
    @property
    def id(self) -> ID:
        return self._id()

    @abc.abstractmethod
    def _id(self) -> ID:
        """Returns the entity ID."""

    def __eq__(self, other: object) -> bool:
        return isinstance(other, self.__class__) and self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)

    def __str__(self) -> str:
        return f"{self.__class__.__name__} {self.id}"  # type: ignore[str-bytes-safe]


class EntityError(Exception):
    """Base classe for entity errors."""

    def __init__(
        self,
        message: str,
        entity: Optional[Entity] = None,
        class_id: Optional[tuple[type[Entity], ID]] = None,
    ):
        if entity:
            message = f"{entity} {message}"
        if class_id:
            message = f"{class_id[0]} {class_id[1]} {message}"  # type: ignore[str-bytes-safe]
        super().__init__(message)


class EntityAlreadyExistError(EntityError):
    """Entity already exists."""

    def __init__(
        self,
        entity: Optional[Entity] = None,
        class_id: Optional[tuple[type[Entity], ID]] = None,
    ):
        super().__init__("already exists", entity, class_id)


class EntityNotFoundError(EntityError):
    """Entity not found."""

    def __init__(
        self,
        entity: Optional[Entity] = None,
        class_id: Optional[tuple[type[Entity], ID]] = None,
    ):
        super().__init__("not found", entity, class_id)
