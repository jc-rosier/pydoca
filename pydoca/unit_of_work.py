import logging
import queue
from contextvars import ContextVar
from types import TracebackType
from typing import Any, Iterator, Optional, Self

import pydantic

from .event import Event
from .port_adapter import inject
from .repository import Repository, Session

logger = logging.getLogger(__name__)

_EVENT_BUS: ContextVar[queue.Queue[Event]] = ContextVar(
    "EVENT_BUS", default=queue.Queue()
)


class EventBus:
    @staticmethod
    def publish_events(events: Iterator[Event]) -> None:
        try:
            event_bus = _EVENT_BUS.get()
            for event in events:
                event_bus.put(event)
        except Exception:
            logger.exception(f"Error publishing events {events}")

    @staticmethod
    def get_event() -> Optional[Event]:
        try:
            return _EVENT_BUS.get().get_nowait()
        except queue.Empty:
            return None

    @staticmethod
    def get_event_block() -> Event:
        return _EVENT_BUS.get().get()


class NotARepositoryError(Exception):
    """If the object is not a repository."""


class DifferentSessionsError(Exception):
    """If the unit of work detects different sessions."""


class UnitOfWorkBase(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(arbitrary_types_allowed=True)

    # TODO: Manage multiple sessions
    _session: Optional[Session] = None

    @property
    def session(self) -> Session:
        if not self._session:
            raise RuntimeError("UnitOfWork session not set.")
        return self._session

    @property
    def repositories(self) -> Iterator[Repository[Any]]:
        for val in dict(self).values():
            if isinstance(val, Repository):
                yield val

    @pydantic.model_validator(mode="before")
    @classmethod
    def inject_repositories(cls, data: dict[str, Repository[Any]]) -> Any:
        if not data:
            data = {}
        for attr_name, attr_info in cls.model_fields.items():
            repository = inject(attr_info.annotation)  # type: ignore
            if not isinstance(repository, Repository):
                raise NotARepositoryError(
                    f"{repository.__class__.__name__} is not a Repository."
                )
            data[attr_name] = repository
        return data

    def __enter__(self) -> Self:
        repo: Repository[Any]
        for repo in dict(self).values():
            session = repo.session
            if not self._session:
                self._session = session
                continue
            if session != self._session:
                raise DifferentSessionsError(
                    "UnitOfWork can not manage different sessions."
                )
        return self

    def __exit__(
        self,
        exc_type: Optional[type[BaseException]] = None,
        exc_value: Optional[BaseException] = None,
        traceback: Optional[TracebackType] = None,
    ) -> None:
        if exc_type:
            self.session.rollback()
        else:
            self.commit()

    def commit(self) -> None:
        try:
            self.session.commit()
        except Exception as exc:
            # Collect the events the clear the Aggregate but do not publish them
            self.collect_events()
            logger.exception(f"Error while committing the session: {exc}")
            raise exc
        else:
            EventBus.publish_events(self.collect_events())

    def collect_events(self) -> Iterator[Event]:
        for repo in self.repositories:
            for i in range(len(repo.events)):
                yield repo.events[i]
