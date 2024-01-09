import pydoca

from .configuration import Configuration

pydoca.bootstrap(
    adapters_config=Configuration,
)
