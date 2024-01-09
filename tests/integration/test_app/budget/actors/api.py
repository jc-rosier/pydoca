import decimal

import fastapi

import tests.integration.test_app.budget.application as application
import tests.integration.test_app.budget.domain as domain

app = fastapi.FastAPI(debug=True)


@app.post("/budget")
def create_budget(payload: application.CreateBudgetCmd) -> domain.Budget:
    return application.CreateBudget().exec(payload)


@app.get("/budget/{budget_id}/calculate_cashflow")
def calculate_cashflow(budget_id: str, currency: domain.Currency) -> decimal.Decimal:
    return application.CalculateCashFlow().exec(
        application.CalculateCashflowCmd(
            budget_id=budget_id,
            currency=currency,
        )
    )


@app.post("/budget/{budget_id}/add_operations")
def add_operations(
    budget_id: str, payload: application.AddToBudgetCmd
) -> domain.Budget:
    return application.AddToBudget().exec(payload)
