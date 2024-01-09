import decimal

import pydoca

from .. import domain
from . import _ports


class CalculateCashflowCmd(pydoca.Command):
    budget_id: str
    currency: domain.Currency


class CalculateCashFlow(pydoca.UseCase):
    # Test simple service injection
    exchange_rate_svc: _ports.ExchangeRateService

    # Test repo injection without uow
    budget_repo: _ports.BudgetRepository

    def exec(self, cmd: CalculateCashflowCmd) -> decimal.Decimal:
        budget: domain.Budget = self.budget_repo.get_by_id(cmd.budget_id)
        cash_flow: decimal.Decimal = budget.calculate_cash_flow_per_month()
        cash_flow = self.exchange_rate_svc.convert_currency(
            cash_flow, budget.currency, cmd.currency
        )
        return cash_flow
