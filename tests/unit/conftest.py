import pytest

import pydoca


@pytest.fixture(autouse=True)
def clear_inject():
    pydoca.clear()
