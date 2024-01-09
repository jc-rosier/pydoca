import decimal

import tests.integration.test_app.budget.application as application
import tests.integration.test_app.budget.domain as domain


class FakeExchangeRateSvc(application.ExchangeRateService):
    def convert_currency(
        self,
        amount: decimal.Decimal,
        current_currency: domain.Currency,
        new_currency: domain.Currency,
    ) -> decimal.Decimal:
        if current_currency is not domain.Currency.CAD:
            raise ValueError(f"Can not convert from {current_currency.value}")

        rates_to_usd = {
            "CAD": 1,
            "EUR": 0.68,
            "USD": 0.75,
        }

        return amount * decimal.Decimal(rates_to_usd[new_currency.name])
