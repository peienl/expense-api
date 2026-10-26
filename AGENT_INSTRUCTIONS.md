# Project Instructions for AI Agents (Axet, etc.)

These are the binding conventions for this repository (`expense-api`). Any AI agent (including Axet) making changes to this codebase MUST follow these rules. If a requested change conflicts with a rule below, flag the conflict instead of silently violating it.

## 1. Pydantic v2 Models

- All request/response schemas live in `app/schemas.py` and must be Pydantic **v2** `BaseModel` subclasses.
- Use Pydantic v2 idioms only:
  - `model_config = ConfigDict(...)` instead of the old `class Config:` inner class.
  - `from_attributes=True` (not `orm_mode = True`) when a schema needs to read from ORM objects.
  - `Field(...)` for validation constraints (`gt`, `ge`, `min_length`, etc.) rather than manual `@validator` checks where a built-in constraint exists.
  - Prefer `model_validate()` / `model_dump()` over the deprecated `.from_orm()` / `.dict()`.
- Keep a clear separation between:
  - **Input schemas** (e.g. `ExpenseCreate`) — only the fields a client is allowed to submit.
  - **Output schemas** (e.g. `ExpenseOut`) — includes server-generated fields (`id`, `created_at`, etc.).
  - Do not reuse the same schema for both input and output unless the shapes are genuinely identical.
- Never expose SQLAlchemy ORM model instances directly from an endpoint — always return a Pydantic schema (set as the route's `response_model`).

## 2. Type Hints

- Every function and method (including test fixtures) must have full type hints on all parameters and the return type — no exceptions for "simple" functions.
- Use the standard library `typing` generics (`list[int]`, `dict[str, Any]`, `Optional[X]` or `X | None`) consistently with the rest of the file.
- Avoid `Any` unless there is genuinely no narrower type available; prefer precise types (e.g. `Session`, `schemas.ExpenseCreate`) over loose ones.
- Public functions in `app/crud.py`, `app/database.py`, and `app/main.py` must have explicit return type annotations — do not rely on inference.
- New dependency-injected parameters (e.g. `db: Session = Depends(get_db)`) must be typed.

## 3. No Business Logic in Routers

- Route handlers in `app/main.py` are HTTP-layer only. They must:
  - Parse/validate input via the schema (FastAPI handles this automatically from the type hint).
  - Call into `app/crud.py` (or a future `app/services.py` layer) to perform the actual work.
  - Translate the result into the appropriate HTTP response (status code, response model).
- Route handlers must **not**:
  - Contain query-building, filtering, calculations, or validation logic beyond what Pydantic provides.
  - Directly construct or manipulate SQLAlchemy model instances.
  - Contain `if`/`else` branches implementing domain rules (e.g. "if amount > 1000, flag as large expense") — that belongs in a CRUD/service function.
- If a new endpoint needs non-trivial logic, add a function to `app/crud.py` (or a new `app/services.py` if the logic grows beyond simple DB access) and have the router call it. The router body should ideally be 1-3 lines.

## 4. Tests for Every Endpoint

- Every route defined in `app/main.py` must have corresponding tests in `tests/test_expenses.py` (or a new `tests/test_<feature>.py` file for new route groups).
- At minimum, each endpoint needs tests covering:
  - The "happy path" (valid input → expected success response and status code).
  - At least one validation/error case (e.g. missing required field, invalid value, not-found resource) → expected 4xx response.
- Use the existing `client` fixture from `tests/conftest.py`, which provides an isolated, auto-cleaned SQLite test database per test. Do not write tests that depend on the real `expenses.db` file or on test execution order.
- When adding a new endpoint, add its tests in the same PR/change — do not defer "add tests later."
- Run `pytest` locally (or via CI) and confirm all tests pass before considering a change complete.

## Summary Checklist for Any New Endpoint/Feature

- [ ] Pydantic v2 input schema (and output schema if different) added to `app/schemas.py`
- [ ] All new functions/methods fully type-hinted
- [ ] Business logic implemented in `app/crud.py` (or a services module), not in the router
- [ ] Router function is a thin wrapper: validate → delegate → respond
- [ ] Happy-path test added
- [ ] At least one error-case test added
- [ ] `pytest` passes locally
