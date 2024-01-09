import pydoca
from pydoca import ID


class WheelChanged(pydoca.Event):
    position: str
    new_reference: str


class Wheel(pydoca.Entity):
    position: str
    reference: str

    def _id(self) -> ID:
        return f"{self.reference}"


class Car(pydoca.AggregateRoot):
    vin: str
    wheels: list[Wheel]

    def _id(self) -> str:
        return self.vin.lower()

    def change_wheel(self, new_wheel: Wheel) -> None:
        wheel_to_replace_idx: int = 0
        for idx, wheel in enumerate(self.wheels):
            if wheel.position == new_wheel.position:
                wheel_to_replace_idx = idx

        self.wheels.pop(wheel_to_replace_idx)
        self.wheels.append(new_wheel)
        self.add_event(
            WheelChanged(
                position=new_wheel.position,
                new_reference=new_wheel.reference,
            )
        )


def test_aggregate_root_events() -> None:
    car = Car(
        vin="vin123",
        wheels=[
            Wheel(reference="ref1", position="top_left"),
            Wheel(reference="ref1", position="top_right"),
            Wheel(reference="ref1", position="bottom_left"),
            Wheel(reference="ref1", position="bottom_right"),
        ],
    )

    car.change_wheel(Wheel(reference="ref2", position="top_left"))

    assert len(car.get_events()) == 1
    assert "ref2" in [wheel.reference for wheel in car.wheels]
