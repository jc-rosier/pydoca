import pytest
import requests

import tests.integration.test_app.budget.domain as domain


@pytest.mark.order(1)
def test_create_budget(fastapi_server, port):
    payload = {
        "budget_title": "Integration Tests",
        "budget_currency": domain.Currency.CAD.value,
    }
    response = requests.post(f"http://localhost:{port}/budget", json=payload)
    assert response.status_code == 200, response.text
    assert response.json() == {
        "title": "Integration Tests",
        "currency": domain.Currency.CAD.value,
        "incomes": [],
        "expenses": [],
        "id": "integration tests",
    }


@pytest.mark.order(2)
def test_add_operations(port):
    payload = {
        "budget_id": "integration tests",
        "operations": [
            {
                "source": "Work",
                "frequency": domain.FrequencyPerYear.MONTHLY.value,
                "amount": 10000,
                "type": "income",
            },
            {
                "source": "Mortgage",
                "frequency": domain.FrequencyPerYear.MONTHLY.value,
                "amount": 5000,
                "type": "expense",
            },
        ],
    }
    response = requests.post(
        f"http://localhost:{port}/budget/integration%20tests/add_operations",
        json=payload,
    )
    assert response.status_code == 200, response.text


@pytest.mark.order(3)
def test_calculate_cashflow(port):
    response = requests.get(
        f"http://localhost:{port}/budget/integration%20tests/calculate_cashflow?currency=United%20States%20dollar"
    )
    assert response.status_code == 200, response.text
    assert response.json() == "3750.00"  #  10000 - 5000 CAD, converted to US
