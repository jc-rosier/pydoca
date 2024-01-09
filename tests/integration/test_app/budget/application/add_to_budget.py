import decimal

import pydantic

import pydoca

from .. import domain
from . import _ports


class Operation(pydoca.ValueObject):
    source: str
    frequency: domain.FrequencyPerYear
    amount: decimal.Decimal
    type: str  # income or expense

    @pydantic.field_validator("type")
    @classmethod
    def check_type_value(cls, v: str) -> str:
        if v not in {"income", "expense"}:
            raise ValueError("Budget operation must be income or expense")
        return v


class AddToBudgetCmd(pydoca.Command):
    budget_id: str
    operations: list[Operation] = []


class AddToBudget(pydoca.UseCase):
    class UnitOfWork:
        budget_repo: _ports.BudgetRepository

    def exec(self, cmd: AddToBudgetCmd) -> domain.Budget:
        with self.uow as uow:
            budget: domain.Budget = uow.budget_repo.get_by_id(cmd.budget_id)
            for ope in cmd.operations:
                if ope.type == "income":
                    budget.add_income(
                        source=ope.source, frequency=ope.frequency, amount=ope.amount
                    )
                if ope.type == "expense":
                    budget.add_expense(
                        source=ope.source, frequency=ope.frequency, price=ope.amount
                    )
            return budget
