import pydoca

from .. import domain
from . import _ports


class CreateBudgetCmd(pydoca.Command):
    budget_title: str
    budget_currency: domain.Currency


class CreateBudget(pydoca.UseCase):
    # Test repo inside uow
    class UnitOfWork:
        budget_repo: _ports.BudgetRepository

    def exec(self, cmd: CreateBudgetCmd) -> domain.Budget:
        budget = domain.Budget(title=cmd.budget_title, currency=cmd.budget_currency)
        return self.uow.budget_repo.save(budget, create=True)
