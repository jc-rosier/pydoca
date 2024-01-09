import collections.abc
from typing import Iterator, Self

import pydoca
import tests.integration.test_app.budget.application as application
import tests.integration.test_app.budget.domain as domain

db = {}


class InMemorySession(pydoca.Session, collections.abc.MutableMapping):
    def __init__(self):
        self.store: dict[str, domain.Budget] = db

    def __setitem__(self, key: str, val: domain.Budget) -> None:
        self.store[key] = val

    def __delitem__(self, key: str) -> None:
        del self.store[key]

    def __getitem__(self, key: str) -> domain.Budget:
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


class InMemoryBudgetRepo(application.BudgetRepository):
    sessionT = InMemorySession

    def get_by_id(self, budget_id: str) -> domain.Budget:
        if budget := self.session.get(budget_id):
            return budget
        else:
            raise pydoca.EntityNotFoundError(class_id=(domain.Budget, budget_id))

    def save(self, budget: domain.Budget, create: bool = False) -> domain.Budget:
        if create and budget.id in self.session:
            raise pydoca.EntityAlreadyExistError(entity=budget)
        self.session[budget.id] = budget
        return budget
