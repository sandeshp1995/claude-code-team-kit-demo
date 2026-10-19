# Project: Harbor Hotel API

A small bookings API for the Harbor Hotel: guests list rooms, book them, and manage their bookings. It is the demo app for the Claude Code Team Kit.

Python 3.12+. Package manager: uv. Framework: FastAPI. Storage: in-memory (`InMemoryStore`), swappable for a database later.

## Commands

- Install deps: `uv sync`
- Run locally: `uv run uvicorn harbor.main:app --reload`
- Test (all): `uv run pytest -q`
- Test (one file): `uv run pytest -q tests/path/test_x.py`
- Test (one test): `uv run pytest -q tests/path/test_x.py::test_name`
- Lint: `uv run ruff check .`  ·  auto-fix: `uv run ruff check --fix .`
- Format: `uv run ruff format .`
- Type check: `uv run mypy src`

After each change: run the single-file test, `ruff check` and `ruff format` on touched files. Before saying a task is done: full test suite and type check must pass.

Always run tools through `uv run ...`. Never `pip install` into the global interpreter.

## Layout

- `src/harbor/`: application code (src layout)
  - `api/`: HTTP layer only: routes (`routes.py`) and request/response schemas (`schemas.py`)
  - `services/`: business rules; no FastAPI imports
  - `repositories/`: data access (`memory.py` today)
  - `models.py`: domain types · `errors.py`: domain exceptions · `auth.py`: bearer-token guest auth
  - `main.py`: app factory and the single domain-error → HTTP mapping
- `tests/`: mirrors `src/harbor/`; shared fixtures and demo tokens in `tests/conftest.py`
- Do not edit: `.venv/`, `uv.lock` by hand

## Conventions

- Type hints on every public function and method. Prefer `X | None` over `Optional[X]`.
- Domain types are dataclasses in `models.py`; API bodies are Pydantic models in `api/schemas.py`. Never return a domain object from a route.
- Money is integer minor units (`*_minor`) plus a `currency` field. Never floats.
- Dates are `datetime.date`; "today" comes from the `get_today` dependency so tests can freeze it.
- Errors: raise `NotFoundError` / `ValidationError` / `ConflictError` from services; `main.py` maps them to 404 / 422 / 409 with `{"error": {"code", "message"}}`. Never raise `HTTPException` from a service.
- A guest may only see or change their own bookings. Return 404, not 403, for someone else's booking.
- Logging: `logger = logging.getLogger(__name__)`; no `print`. Never log tokens.
- Docstrings for public modules, classes, and functions: one-line summary, then details only if non-obvious.

## Testing

- pytest only. Plain `assert`. Arrange / act / assert separated by blank lines.
- Test names describe behaviour: `test_other_guest_gets_404_for_booking`.
- Service rules get service tests (`tests/services/`); every route gets API tests for success, validation failure, and unauthorised access (`tests/api/`).
- Use the `client` and `store` fixtures; never share state between tests.
- Every bug fix gets a regression test that fails before the fix.

## Workflow

- Before a non-trivial change, state a short plan and the files you will touch.
- Small, reviewable diffs. Do not reformat untouched files.
- Never commit, push, or open a pull request unless asked.
- Commit messages: Conventional Commits with the ticket key, e.g. `feat: HB-3 cancel a booking`.

## Boundaries

- Never read or print `.env*` files or secrets.
- Ask before adding a dependency; add it with `uv add` so the lockfile updates.
- Ask before changing a public API contract (route, field, status code).

## Team notes

- `auth.py` uses static demo tokens: `demo-token-alice` and `demo-token-bob` (guests) and `demo-token-staff` (front desk, can read every guest's arrivals). All are intentionally public and demo-only; never copy them into a real deployment.
