import abc
import decimal

import pydoca

from .. import domain


class BudgetRepository(pydoca.Repository):
    @abc.abstractmethod
    def get_by_id(self, budget_id: str) -> domain.Budget:
        """Returns a budget if it exists or raise error.

        Raises:
            EntityNotFoundError: If raise_if_not_exist is True and the budget is not found.
        """

    @abc.abstractmethod
    def save(self, budget: domain.Budget, create: bool = False) -> domain.Budget:
        """Saves the budget.

        If create is True, raise an error if already exists in the repo.
        """


class ExchangeRateService(pydoca.Service):
    @abc.abstractmethod
    def convert_currency(
        self,
        amount: decimal.Decimal,
        current_currency: domain.Currency,
        new_currency: domain.Currency,
    ) -> decimal.Decimal:
        """Converts the amount to the new currency."""
