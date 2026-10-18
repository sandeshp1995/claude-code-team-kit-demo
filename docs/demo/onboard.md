> Output of `/onboard` from the Claude Code Team Kit, run on this repo at v0.2.0 and kept as generated. Some gotchas it lists (the stale README, the undocumented staff token) were fixed in the same pull request that added this file.

# Welcome to Harbor Hotel API

Everything below comes from reading the code. I did not run the install, server, tests, lint or type check. I also didn't run `uv sync`, which `uv.lock` implies, so treat the commands as unverified.

## In one paragraph
Harbor is a small FastAPI bookings API for a fictional hotel. Guests list rooms, book them, read their own bookings and cancel them. Front-desk staff can list a day's arrivals. It is the demo app for the Claude Code Team Kit (`README.md`, `CLAUDE.md:3`). It uses Python 3.12+, uv, FastAPI and Pydantic, with an in-memory store, pytest, ruff and mypy.

## Map
| Area | Path | What lives here |
|---|---|---|
| App factory and error mapping | `src/harbor/main.py:18` | `create_app(store)`, plus the one handler that turns domain errors into HTTP responses (`main.py:24`) |
| Guest routes | `src/harbor/api/routes.py` | `/rooms`, `/bookings`, `/bookings/{id}`, `/bookings/{id}/cancel`, and the `get_store` and `get_today` dependencies |
| Staff routes | `src/harbor/api/staff.py:21` | `GET /staff/arrivals?day=` |
| Schemas | `src/harbor/api/schemas.py` | Pydantic in/out models, each with `from_domain` |
| Business rules | `src/harbor/services/bookings.py`, `services/arrivals.py` | No FastAPI imports |
| Storage | `src/harbor/repositories/memory.py` | `InMemoryStore` plus the three seeded rooms (`memory.py:7`) |
| Domain types | `src/harbor/models.py` | `Room`, `Booking`, `Arrival`, `BookingStatus` |
| Errors | `src/harbor/errors.py` | `NotFoundError`, `ValidationError` and `ConflictError` |
| Auth | `src/harbor/auth.py` | Static demo bearer tokens (`auth.py:12`) and the guest and staff dependencies |
| Tests | `tests/{api,services}/`, `tests/conftest.py` | Mirror `src/`. `conftest.py` has the `store` and `client` fixtures and a frozen `TODAY` of 2026-11-02 |
| Kit skills | `.claude/skills/` | The free skills are committed. The Pro ones are gitignored (`.gitignore`). |

## How a request flows
This traces `POST /bookings/{id}/cancel`.
1. `src/harbor/main.py:35` builds the module-level `app`, which includes both routers (`main.py:21-22`).
2. `api/routes.py:61` is the handler. FastAPI resolves its dependencies: `Guest`, `Store` and `Today`.
3. `auth.py:21` `current_guest` reads the `Authorization` header and checks it against `DEMO_TOKENS` using `hmac.compare_digest`. It raises 401 on failure and returns an id such as `guest-alice`.
4. `routes.py:18` `get_store` returns `request.app.state.store`, which was set at `main.py:20`.
5. `routes.py:26` `get_today` returns `date.today()`. Tests override it.
6. `routes.py:63` calls `booking_service.cancel_booking(...)`.
7. `services/bookings.py:73` calls `get_booking_for_guest`. It raises `NotFoundError` for a missing booking and also for one owned by someone else (`bookings.py:66`).
8. `bookings.py:74-79` raises `ConflictError` if the booking isn't confirmed or if check-in is less than 2 days away (`CANCEL_NOTICE_DAYS`, `bookings.py:12`).
9. `bookings.py:82-83` builds a copy with `dataclasses.replace`. The copy has status `CANCELLED` and `refund_minor` equal to `total_minor`, and `store.update_booking` saves it (`memory.py:28`).
10. `routes.py:66` returns `BookingOut.from_domain(...)` (`schemas.py:46`). If a service had raised, `main.py:24-30` would map `NotFoundError` to 404, `ValidationError` to 422, `ConflictError` to 409, and anything else to 400. The body is `{"error": {"code", "message"}}`.

## Key concepts and vocabulary
- **`*_minor`**: money as integer minor units (cents). `currency` is hard-coded to "USD" in the schemas (`schemas.py:14`).
- **Arrival**: a confirmed booking whose check-in is a given day, with the room kind, for the front desk (`models.py:38`).
- **Cancel notice window**: cancelling is allowed only 2 or more days before check-in, and the refund is then 100% (`bookings.py:81`).
- **Guest vs staff**: both come from the same token table. Staff is the set `STAFF_IDS` (`auth.py:18`).
- **HB-n**: ticket keys that appear in commit messages, e.g. `HB-3` for cancel and `HB-5` for arrivals.
- **Team Kit commands** (`/review`, `/onboard`, `/commit-msg` and others): the product this repo demos.

## Running it
Commands are taken from `CLAUDE.md:9-19` and not verified.
- Install: `uv sync`
- Run: `uv run uvicorn harbor.main:app --reload`, then open http://127.0.0.1:8000/docs
- Test: `uv run pytest -q`. For one file use `uv run pytest -q tests/api/test_bookings_api.py`.
- Lint and format: `uv run ruff check .` and `uv run ruff format .`
- Types: `uv run mypy src`
- Always run tools through `uv run`.
- Demo tokens are `demo-token-alice`, `demo-token-bob` and `demo-token-staff`.
- To try it, send `Authorization: Bearer demo-token-alice`.

## Where the action is
This is a heuristic. The repo has about 10 commits, all by one author, `sandeshp1995`. Ask them about anything.
- In the last 3 months the most-touched files were `models.py`, `api/schemas.py`, `services/bookings.py`, `repositories/memory.py` and `tests/api/test_bookings_api.py`.
- The history runs: v0.1.0, then cancel booking (HB-3), then arrivals (HB-5), then review fixes.

## Gotchas
- **README is stale.** Its API table lists only 3 routes. The code also has cancel and staff arrivals (`README.md`). It also links `CHANGELOG.md` and `docs/demo/`, and `docs/` doesn't exist in this checkout.
- **Auth.** The tokens are intentionally public (`CLAUDE.md:58`). The 403 for non-staff on `/staff/arrivals` comes from `auth.py:35`.
- **The module-level `app`** (`main.py:35`) shares one global store. Tests use `create_app(store)` instead, so don't import `app` in tests.
- **Error status codes.** Auth failures raise `HTTPException` in `auth.py`, which is allowed there and not in services. An unmapped `HarborError` returns 400 (`main.py:26`).
- **Cancel and arrivals edge cases** (my inference, not tested). Cancelling a booking whose check-in is in the past gives a ConflictError, because the day count is negative. `arrivals_on` raises `NotFoundError` (a 404) if a booking points at a missing room (`arrivals.py:18`). That would be misleading for a data bug.
- **No concurrency control.** The availability check and the insert aren't atomic (`bookings.py:42-59`). This is fine for a single-process demo.
- **Do not hand-edit** `uv.lock` or `.venv/`. Ask before adding dependencies or changing a route, field or status code (`CLAUDE.md:51-53`).
- **Workflow rules** (`CLAUDE.md:44-48`): never commit or push unless asked, and use Conventional Commits with the ticket key. One history commit has a placeholder message ("wip: HB-5 review fixes", `c2023b9`).
- **`.claude/rules/python-api.md`** contains generic placeholders such as `<Pydantic models | DRF serializers>`. It is a template, so treat it as guidance rather than repo-specific rules.

## Good first tasks
1. Trace the flow above with the `client` fixture. Read `tests/api/test_bookings_api.py` and `tests/conftest.py`, then run one test.
2. Add a regression test for cancelling a booking whose check-in has already passed, and decide whether 409 is the right behaviour. This is a contract question, so ask first.
3. Update the README API table to include `POST /bookings/{id}/cancel` and `GET /staff/arrivals`, and fix the broken doc links.
4. Add a service test for `arrivals_on` ordering and for excluding cancelled bookings. First check `tests/services/test_arrivals.py` for existing coverage.
5. Add a `Room` list test for sort order (`memory.py:20`) in `tests/api/`.
