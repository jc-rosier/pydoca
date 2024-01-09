from typing import Optional

from .port_adapter import AdaptersConfig


def bootstrap(adapters_config: Optional[type[AdaptersConfig]] = None) -> None:
    if adapters_config:
        adapters_config()
    return None
