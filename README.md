# Expense API

A minimal FastAPI starter for tracking expenses, backed by SQLite.

## Features

- `POST /expenses` — create a new expense (`description`, `amount`, optional `category`)
- `GET /expenses` — list expenses (supports `skip` / `limit` pagination)
- SQLite storage via SQLAlchemy ORM
- Automatic interactive API docs at `/docs` (Swagger UI) and `/redoc`
- Test suite built with `pytest` and FastAPI's `TestClient`

## Project Structure

```
expense-api/
├── app/
│   ├── __init__.py
│   ├── main.py        # FastAPI app & routes
│   ├── database.py    # SQLAlchemy engine/session setup
│   ├── models.py      # ORM models
│   ├── schemas.py     # Pydantic request/response schemas
│   └── crud.py         # Database access functions
├── tests/
│   ├── __init__.py
│   ├── conftest.py    # Test fixtures (isolated SQLite test DB)
│   └── test_expenses.py
├── requirements.txt
├── pytest.ini
└── README.md
```

## Setup

1. Create and activate a virtual environment (recommended):

   ```bash
   python -m venv .venv
   .venv\Scripts\activate   # Windows
   # source .venv/bin/activate  # macOS/Linux
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

## Running the API

```bash
uvicorn app.main:app --reload
```

The API will be available at `http://127.0.0.1:8000`. Visit `http://127.0.0.1:8000/docs` for interactive documentation.

A SQLite database file `expenses.db` will be created automatically in the project directory on first run.

## Example Usage

Create an expense:

```bash
curl -X POST http://127.0.0.1:8000/expenses \
  -H "Content-Type: application/json" \
  -d '{"description": "Lunch", "amount": 12.5, "category": "Food"}'
```

List expenses:

```bash
curl http://127.0.0.1:8000/expenses
```

## Running Tests

```bash
pytest
```

Tests use an isolated SQLite database file (`test_expenses.db`) that is created and removed automatically for each test run, so they do not affect your main `expenses.db`.
