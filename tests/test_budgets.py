"""Tests for the /budgets and /alerts endpoints."""
from datetime import datetime, timezone

# Expenses are always created with `created_at = now()`, so budget/alert
# tests that check spend-vs-limit must use the *current* year/month to
# line up with when the test's expenses are actually recorded.
_NOW = datetime.now(timezone.utc)
_YEAR = _NOW.year
_MONTH = _NOW.month
_MONTH_STR = f"{_YEAR:04d}-{_MONTH:02d}"


def test_create_budget(client):
    payload = {"category": "Food", "year": 2025, "month": 6, "monthly_limit": 300.0}
    response = client.post("/budgets", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["category"] == "Food"
    assert data["year"] == 2025
    assert data["month"] == 6
    assert data["monthly_limit"] == 300.0
    assert "id" in data
    assert "created_at" in data


def test_create_duplicate_budget_returns_409(client):
    payload = {"category": "Food", "year": 2025, "month": 6, "monthly_limit": 300.0}
    first = client.post("/budgets", json=payload)
    assert first.status_code == 201

    second = client.post("/budgets", json=payload)
    assert second.status_code == 409


def test_create_budget_invalid_month_returns_422(client):
    payload = {"category": "Food", "year": 2025, "month": 13, "monthly_limit": 300.0}
    response = client.post("/budgets", json=payload)
    assert response.status_code == 422


def test_create_budget_invalid_limit_returns_422(client):
    payload = {"category": "Food", "year": 2025, "month": 6, "monthly_limit": -10}
    response = client.post("/budgets", json=payload)
    assert response.status_code == 422


def test_read_budget_status_empty_when_no_budgets(client):
    response = client.get("/budgets/2025-06")
    assert response.status_code == 200
    assert response.json() == []


def test_read_budget_status_invalid_month_format_returns_422(client):
    response = client.get("/budgets/2025-6")
    assert response.status_code == 422

    response = client.get("/budgets/not-a-month")
    assert response.status_code == 422


def test_read_budget_status_reflects_spend(client):
    client.post(
        "/budgets",
        json={"category": "Food", "year": _YEAR, "month": _MONTH, "monthly_limit": 100.0},
    )
    client.post("/expenses", json={"description": "Groceries", "amount": 40.0, "category": "Food"})
    client.post("/expenses", json={"description": "Dinner", "amount": 30.0, "category": "Food"})

    response = client.get(f"/budgets/{_MONTH_STR}")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    status = data[0]
    assert status["category"] == "Food"
    assert status["monthly_limit"] == 100.0
    assert status["total_spent"] == 70.0
    assert status["remaining"] == 30.0
    assert status["percent_used"] == 70.0
    assert status["is_overspent"] is False
    assert status["overspend_amount"] == 0.0


def test_read_alerts_empty_when_under_threshold(client):
    client.post(
        "/budgets",
        json={"category": "Food", "year": _YEAR, "month": _MONTH, "monthly_limit": 100.0},
    )
    client.post("/expenses", json={"description": "Snack", "amount": 10.0, "category": "Food"})

    response = client.get(f"/alerts/{_MONTH_STR}")
    assert response.status_code == 200
    assert response.json() == []


def test_read_alerts_warning_level(client):
    client.post(
        "/budgets",
        json={"category": "Food", "year": _YEAR, "month": _MONTH, "monthly_limit": 100.0},
    )
    client.post("/expenses", json={"description": "Groceries", "amount": 85.0, "category": "Food"})

    response = client.get(f"/alerts/{_MONTH_STR}")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["category"] == "Food"
    assert data[0]["level"] == "warning"


def test_read_alerts_exceeded_level(client):
    client.post(
        "/budgets",
        json={"category": "Food", "year": _YEAR, "month": _MONTH, "monthly_limit": 100.0},
    )
    client.post("/expenses", json={"description": "Feast", "amount": 150.0, "category": "Food"})

    response = client.get(f"/alerts/{_MONTH_STR}")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["category"] == "Food"
    assert data[0]["level"] == "exceeded"


def test_read_alerts_invalid_month_format_returns_422(client):
    response = client.get("/alerts/bad-month")
    assert response.status_code == 422
