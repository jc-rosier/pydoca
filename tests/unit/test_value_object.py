import pydantic
import pytest

import pydoca


class FakeValueObject(pydoca.ValueObject):
    attribute1: int
    attribute2: str


def test_value_object_immutable() -> None:
    vo = FakeValueObject(attribute1=10, attribute2="test")
    with pytest.raises(pydantic.ValidationError):
        vo.attribute1 = 20


def test_value_object_equality() -> None:
    vo1 = FakeValueObject(attribute1=10, attribute2="test")
    vo2 = FakeValueObject(attribute1=10, attribute2="test")
    vo3 = FakeValueObject(attribute1=20, attribute2="test")

    assert vo1 == vo2  # Same attributes, so they should be equal
    assert vo1 != vo3  # Different attribute value


def test_value_object_hash() -> None:
    vo1 = FakeValueObject(attribute1=10, attribute2="test")
    vo2 = FakeValueObject(attribute1=10, attribute2="test")
    vo3 = FakeValueObject(attribute1=20, attribute2="test")

    assert hash(vo1) == hash(
        vo2
    )  # Same attributes, so their hash values should be equal
    assert hash(vo1) != hash(vo3)  # Different attribute value


def test_value_object_extra_attributes() -> None:
    with pytest.raises(pydantic.ValidationError):
        FakeValueObject(attribute1=10, attribute2="test", extra_attribute=30)  # type: ignore[call-arg]


def test_direct_use_of_value_object() -> None:
    with pytest.raises(TypeError):
        pydoca.ValueObject()
