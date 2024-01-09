# pydoca

Domain-Oriented Clean Architecture python library.

A marriage of Uncle Bob's Clean Architecture and Eric Evan's Domain-Driven Design, for Python developers.

[![CI](https://github.com/jc-rosier/pydoca/actions/workflows/ci.yml/badge.svg?event=push&branch=main)](https://github.com/jc-rosier/pydoca/actions?query=event%3Apush+branch%3Amain+workflow%3ACI)
[![Coverage](https://coverage-badge.samuelcolvin.workers.dev/jc-rosier/pydoca.svg)](https://coverage-badge.samuelcolvin.workers.dev/redirect/jc-rosier/pydoca)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](https://github.com/jc-rosier/pydantic/blob/main/LICENSE)

## Quickstart

Install using `pip install pydoca`

## How to use

*Disclaimer: This is a very trivial example, a more complex one can be found in the integration tests.*

Create your domain first.

```python
# app/domain/car.py
from typing import Literal

import pydoca


class TireChanged(pydoca.Event):
    position: str
    reference: str


class Tire(pydoca.Entity):
    reference: str
    position: Literal["front-right", "front-left", "back-right", "back-left"]
    wear: float = 1.0
    def _id(self) -> str:
        return f"{self.reference}-{self.position}".lower()


class Car(pydoca.AggregateRoot):
    vin: str
    tires: list[Tire] = []
    def _id(self) -> str:
        return self.vin.lower()

    def change_tire(self, new_tire: Tire) -> None:
        tire_to_change_idx = next(idx for idx, tire in enumerate(self.tires) if tire.position == new_tire.position)
        self.tires.pop(tire_to_change_idx)
        self.tires.append(new_tire)
        self.add_event(TireChanged(position=new_tire.position, reference=new_tire.reference))
```

Then your use case. Your domain and your use cases should not depend on external dependencies.

*-> dependency direction*
actors|adapters -> application -> domain

```python
# app/application/change_tire.py
import abc

import pydoca

from app.domain.car import Car, Tire


class CarRepo(pydoca.Repository):

    @abc.abstractmethod
    def get_by_id(self, car_id: str) -> Car:
        """Gets a car or raises EntityNotFoundError."""

    @abc.abstractmethod
    def save(self, car: Car) -> Car:
        """Saves a car."""

class ChangeTireCmd(pydoca.Command):
    car_id: str
    reference: str
    position: str


class ChangeTire(pydoca.UseCase):
    class UnitOfWork:
        car_repo: CarRepo

    def exec(self, cmd: ChangeTireCmd) -> Car:
        with self.uow as uow:  # The UOW will automatically push your aggregates events to the event bus.
            car: Car = uow.car_repo.get_by_id(cmd.car_id)
            car.change_tire(Tire(position=cmd.position, reference=cmd.reference))
        return car
```

Now you need an actor, your application entry point calling the use case.
Let's use FastAPI for example.

```python
# app/actors/api.py
import fastapi

from app.application.change_tire import ChangeTire, ChangeTireCmd
from app.domain.car import Car

app = fastapi.FastAPI()


@app.put("/car/{car_id}/change_tire")
def change_tire(payload: ChangeTireCmd) -> Car:
    return ChangeTire().exec(payload)
```

Last step is to implement the car repository in adapters and configure the project.

```python
# app/adapters/inmemory_car_repo.py
import collections.abc
from typing import Iterator, Self

import pydoca

from app.application.change_tire import CarRepository
from app.domain.car import Car, Tire


db = {
    "fake_car": Car(
        vin="fake_car",
        tires=[
            Tire(reference="michelinf", position="front-right"),
            Tire(reference="michelinb", position="back-right"),
            Tire(reference="michelinf", position="front-left"),
            Tire(reference="michelinb", position="back-left", wear=0.1),
        ]
    )
}


class InMemorySession(pydoca.Session, collections.abc.MutableMapping):

    def __init__(self):
        self.store: dict[str, Car] = db

    def __setitem__(self, key: str, val: Car) -> None:
        self.store[key] = val

    def __delitem__(self, key: str) -> None:
        del self.store[key]

    def __getitem__(self, key: str) -> Car:
        return self.store[key]

    def __len__(self) -> int:
        return len(self.store)

    def __iter__(self) -> Iterator[str]:
        return iter(self.store)

    @classmethod
    def start(cls) -> Self:
        return cls()

    @classmethod
    def url(cls) -> str:
        return "//memory"

    def commit(self) -> None:
        print("Commit")

    def rollback(self) -> None:
        print("Rollback")


class InMemoryCarRepo(CarRepository):
    sessionT = InMemorySession

    def get_by_id(self, car_id: str) -> Car:
        if car := self.session.get(car_id):
            return car
        else:
            raise pydoca.EntityNotFoundError(class_id=(Car, car_id))

    def save(self, car: Car) -> Car:
        self.session[car.id] = car
        return car
```

```python
# app/local_configuration.py
import pydoca

from app.adapters.inmemory_car_repo import InMemoryCarRepo


class Configuration(pydoca.AdaptersConfig):
    CarRepository = InMemoryCarRepo
```

```python
# app/main.py
import pydoca
import uvicorn

from app.local_configuration import Configuration


if __name__ == "__main__":
    pydoca.bootstrap(adapters_config=Configuration)
    uvicorn.run("app.actors.api:app")
```

Then you can execute the main file and visit http://localhost:8080/docs and use the swagger to change the back-left tire of fake_car:)

```bash
pip install fastapi uvicorn pydoca
python app/main.py
```

## Development

TODO (In order of importance):

- publish to pypi
- *(Alpha version at this point)*
- Fix mypy for pytest (remove pre-config tests exclusion)
- 100% tests coverage
- Fix type hints and Pycharm autocompletion features
- Re-work events, maybe context python bus not the good solution
- mkdocs
- Allow to hide some Command attributes in the model and be able to set them later
- binary to analyze code like mypy and give errors/warnings/feedbacks
- Add modules for easy integration with fastapi, cli tools, aws lambda etc.
- UnitOfWork manages multiple sessions?
- Improve tests, integration with real DBs, multiple actors etc.
- *(Beta version at this point)*
