import abc
import functools
import inspect
import itertools
from types import MappingProxyType
from typing import Any, Callable, Generic, Optional, Self, TypeVar, cast

from .aggregate_root import AggregateRoot
from .event import Event
from .port_adapter import Port

AggregateRootT = TypeVar("AggregateRootT", bound=AggregateRoot)


class Session(abc.ABC):
    @classmethod
    @abc.abstractmethod
    def start(cls) -> Self:
        """Starts the session."""

    @classmethod
    @abc.abstractmethod
    def url(cls) -> str:
        """Returns the session url."""

    @abc.abstractmethod
    def commit(self) -> None:
        """Commits the session."""

    @abc.abstractmethod
    def rollback(self) -> None:
        """Rollbacks changes if any."""

    def __eq__(self, other: Any) -> bool:
        """Compares two sessions."""
        return isinstance(other, self.__class__) and self.url() == other.url()


TWrap = TypeVar("TWrap", bound=Callable[..., Any])


class Repository(Generic[AggregateRootT], Port):
    """Repository interface."""

    sessionT: type[Session]
    events: list[Event]
    _session: Optional[Session] = None

    def __init__(self) -> None:
        self.events = []

    @property
    def session(self) -> Session:
        if self._session:
            return self._session
        self._session = self.sessionT.start()
        return self._session

    def set_session(self, session: Session) -> None:
        self._session = session

    def __init_subclass__(cls, **kwargs: Any) -> None:
        super().__init_subclass__(**kwargs)  # Call for Port
        if isinstance(cls, abc.ABC):
            return  # Assumes every non ABC class is a real repository implementation
        for name, fn in inspect.getmembers(cls, inspect.isfunction):
            if name.startswith("__") and name.endswith("__"):
                continue
            parameters: MappingProxyType[str, inspect.Parameter] = inspect.signature(
                fn
            ).parameters
            for parameter in parameters.values():
                if inspect.isclass(parameter.annotation) and issubclass(
                    parameter.annotation, AggregateRoot
                ):
                    setattr(cls, name, cls.track_events(fn))

    @classmethod
    def track_events(cls, func: TWrap) -> TWrap:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            for param in itertools.chain(args, kwargs.values()):
                if isinstance(param, AggregateRoot):
                    args[0].events.extend(param.get_events())
                    param.clear_events()
                if isinstance(param, list):
                    for elem in param:
                        if isinstance(elem, AggregateRoot):
                            args[0].events.extends(elem.get_events())
                            elem.clear_events()
            return func(*args, **kwargs)

        return cast(TWrap, wrapper)
