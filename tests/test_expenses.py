"""Tests for the /expenses endpoints."""


def test_read_root(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Expense API is running"}


def test_create_expense(client):
    payload = {"description": "Lunch", "amount": 12.5, "category": "Food"}
    response = client.post("/expenses", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["description"] == "Lunch"
    assert data["amount"] == 12.5
    assert data["category"] == "Food"
    assert "id" in data
    assert "created_at" in data


def test_create_expense_without_category(client):
    payload = {"description": "Coffee", "amount": 3.5}
    response = client.post("/expenses", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["category"] is None


def test_create_expense_invalid_amount(client):
    payload = {"description": "Invalid", "amount": -5}
    response = client.post("/expenses", json=payload)
    assert response.status_code == 422


def test_create_expense_missing_description(client):
    payload = {"amount": 10}
    response = client.post("/expenses", json=payload)
    assert response.status_code == 422


def test_create_expense_unknown_category_returns_422(client):
    payload = {"description": "Mystery item", "amount": 5.0, "category": "NotARealCategory"}
    response = client.post("/expenses", json=payload)
    assert response.status_code == 422


def test_get_expenses_empty(client):
    response = client.get("/expenses")
    assert response.status_code == 200
    assert response.json() == []


def test_get_expenses_after_create(client):
    client.post("/expenses", json={"description": "Taxi", "amount": 20.0})
    client.post("/expenses", json={"description": "Hotel", "amount": 150.0})

    response = client.get("/expenses")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    descriptions = {item["description"] for item in data}
    assert descriptions == {"Taxi", "Hotel"}


def test_get_expenses_pagination(client):
    for i in range(5):
        client.post("/expenses", json={"description": f"Item {i}", "amount": 1.0 + i})

    response = client.get("/expenses", params={"skip": 1, "limit": 2})
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
