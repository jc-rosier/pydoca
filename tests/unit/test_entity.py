import pydoca


class TestEntity(pydoca.Entity):
    name: str

    def _id(self) -> str:
        return self.name


def test_entity_id() -> None:
    entity = TestEntity(name="test")
    assert entity.id == "test"


def test_entity_eq() -> None:
    entity1 = TestEntity(name="test")
    entity2 = TestEntity(name="test")
    entity3 = TestEntity(name="")
    assert entity1 == entity2
    assert entity1 != entity3


def test_entity_hash() -> None:
    entity = TestEntity(name="test")
    assert hash(entity) == hash("test")


def test_entity_str() -> None:
    entity = TestEntity(name="test")
    assert str(entity) == "TestEntity test"
