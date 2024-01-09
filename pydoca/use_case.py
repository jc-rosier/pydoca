import abc
from typing import Any, ClassVar, Optional

import pydantic

from .port_adapter import Port, inject
from .unit_of_work import UnitOfWorkBase
from .value_object import ValueObject


class UnitOfWorkNotDefined(Exception):
    """When the UnitOfWork class in not defined in the Use Case."""


class Command(ValueObject):
    """Represents an intention to perform a specific action or operation within the domain.

    Encapsulates the parameters and details needed to execute a use case.
    """


class Service(Port):
    """Service interface."""


UnitOfWork = UnitOfWorkBase


class UseCase(pydantic.BaseModel):
    __uow__: ClassVar[Optional[type[UnitOfWork]]] = None
    model_config = pydantic.ConfigDict(arbitrary_types_allowed=True)

    @classmethod
    def __pydantic_init_subclass__(cls, **kwargs: Any) -> None:
        uow_cls: Optional[type[UnitOfWork]] = cls.__dict__.get("UnitOfWork")
        if not uow_cls:
            return

        repositories: dict[str, Any] = {
            repo_name: (repo_type, None)
            for repo_name, repo_type in uow_cls.__annotations__.items()
        }
        cls.__uow__ = pydantic.create_model(
            "UnitOfWork",
            **repositories,
            __base__=UnitOfWorkBase,
        )

    @property
    def uow(self) -> UnitOfWork:
        if not self.__uow__:
            raise UnitOfWorkNotDefined("UnitOfWork class not defined.")
        return self.__uow__()

    @pydantic.model_validator(mode="before")
    @classmethod
    def inject_providers(cls, data: Any) -> Any:
        if not data:
            data = {}
        for attr_name, attr_info in cls.model_fields.items():
            if attr_name not in data:
                # Assumes the attribute needs to be injected.
                data[attr_name] = inject(attr_info.annotation)  # type: ignore
        return data

    @abc.abstractmethod
    def exec(self, cmd: Command) -> Any:
        """Executes the Use Case."""
