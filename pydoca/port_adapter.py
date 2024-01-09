"""Port/Adapter architecture pattern."""
import abc
import inspect
import logging
from typing import Any, Callable, ClassVar, Optional, Self

logger = logging.getLogger(__name__)

PortClassName = str


class Port(abc.ABC):
    """Port.

    Abstract classes inheriting Port are considered Port in the Port/Adapter pattern.
    They should be defined in the application layer of your project. One layer above your domain
    and used in your Use Cases.

    Classes inheriting and implementing those abstract classes are considered the adapters,
    and should be defined in the adapters, outer layer of your project, alongside the actors.

    Attributes:
        _registry: Keeps track of the Port classes so we can find them using only their names.
    """

    _registry: ClassVar[dict[PortClassName, type[Self]]] = {}

    def __init_subclass__(cls, **kwargs: Any) -> None:
        if cls.__name__ in ["Repository", "Service"] or not inspect.isabstract(cls):
            # Do not register our bases Repository and Service abc classes, they are part of pydoca.
            # Do not register real implementations (adapters) to the ports registry as there
            # __init_subclass__ is also triggered here.
            return

        super().__init_subclass__(**kwargs)
        # Should be an abstract class inheriting `Port` declared as part of the user application ports.
        cls._registry[cls.__name__] = cls
        logger.info(f"Register {cls.__name__} port")


PortType = type[Port]


class AdapterNotConfiguredError(Exception):
    def __init__(self, port: PortType) -> None:
        super().__init__(f"Adapter for {port.__name__} port not configured")


class PortNotFoundError(Exception):
    def __init__(self, port: PortClassName) -> None:
        super().__init__(f"Port class {port} not found.")


Adapter = object | Any
AdapterFactory = Callable[[], Adapter]

_ADAPTERS_CONFIGURATION: dict[PortType, AdapterFactory | Adapter] = {}


def bind(port: PortType, adapter: AdapterFactory | Adapter) -> None:
    _ADAPTERS_CONFIGURATION[port] = adapter
    logger.info(f"Bind {port} port to {adapter} adapter")


def clear() -> None:
    _ADAPTERS_CONFIGURATION.clear()


def inject(port: PortType) -> Adapter:
    adapter: Optional[AdapterFactory | Adapter] = _ADAPTERS_CONFIGURATION.get(port)
    if not adapter:
        raise AdapterNotConfiguredError(port)

    if callable(adapter):
        return adapter()
    else:
        return adapter


class AdaptersConfig:
    """Adapters configuration to automatically bind them when bootstrap.

    class DevConfiguration(pydoca.AdaptersConfig):
        YourRepository = adapters.SQLiteRepo
        YourService = adapters.FakeService

    pydoca.bootstrap(adapters_config=DevConfiguration)

    This configuration alongside bootstrap will bind YourRepository port to SQLiteRepo adapter and
    YourService port to FakeService adapter.
    """

    def __init__(self) -> None:
        for port_name, adapter_class in [
            (key, val)
            for key, val in self.__class__.__dict__.items()
            if not key.startswith("__")
        ]:
            if port_name in Port._registry:
                bind(Port._registry[port_name], adapter_class)
            else:
                raise PortNotFoundError(port_name)

    def __init_subclass__(cls, **kwargs: Any):
        # Forces subclass to trigger super init
        cls.__init__ = lambda self: super(cls, self).__init__()  # type: ignore[method-assign]
