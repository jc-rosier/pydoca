"""Very simplistic domain representing a budget based on incomes and expenses."""
import decimal
import enum

import pydoca


class Currency(str, enum.Enum):
    """ISO 4217 currency codes."""

    CAD = "Canadian dollar"
    EUR = "Euro"
    USD = "United States dollar"


class FrequencyPerYear(enum.Enum):
    YEARLY = 1
    MONTHLY = 12
    SEMI_MONTHLY = 24
    BI_WEEKLY = 26
    WEEKLY = 52
    DAILY = 365


class Income(pydoca.Entity):
    """Money a person or entity receives in exchange for their labor or investment."""

    source: str
    frequency: FrequencyPerYear
    amount: decimal.Decimal

    def _id(self) -> str:
        return self.source.lower()


class Expense(pydoca.Entity):
    """Payment for an item, service, or other category of costs."""

    source: str
    frequency: FrequencyPerYear
    price: decimal.Decimal

    def _id(self) -> str:
        return self.source.lower()


class IncomeAdded(pydoca.Event):
    source: str


class ExpenseAdded(pydoca.Event):
    source: str


class Budget(pydoca.AggregateRoot):
    title: str
    currency: Currency
    incomes: list[Income] = []
    expenses: list[Expense] = []

    def _id(self) -> str:
        return self.title.lower()

    def add_income(
        self, source: str, frequency: FrequencyPerYear, amount: decimal.Decimal
    ) -> None:
        income = Income(source=source, frequency=frequency, amount=amount)
        if income in self.incomes:
            raise pydoca.EntityAlreadyExistError(income)
        self.incomes.append(income)
        self.add_event(IncomeAdded(source=source))

    def add_expense(
        self, source: str, frequency: FrequencyPerYear, price: decimal.Decimal
    ) -> None:
        expense = Expense(source=source, frequency=frequency, price=price)
        if expense in self.expenses:
            raise pydoca.EntityAlreadyExistError(expense)
        self.expenses.append(expense)
        self.add_event(ExpenseAdded(source=source))

    def calculate_cash_flow_per_month(self) -> decimal.Decimal:
        total = decimal.Decimal(0)

        for income in self.incomes:
            total += income.amount * income.frequency.value / 12

        for expense in self.expenses:
            total -= expense.price * expense.frequency.value / 12

        return total
