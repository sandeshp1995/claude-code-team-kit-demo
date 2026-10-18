> Output of `/explain src/harbor/services/bookings.py` from the Claude Code Team Kit, run on this repo at v0.2.0 and kept as generated. Some gotchas it lists (the stale README, the undocumented staff token) were fixed in the same pull request that added this file.

# `src/harbor/services/bookings.py`

**Purpose:** This file holds the booking rules: creating a booking, fetching one for its owner, and cancelling one. It has no FastAPI imports (`bookings.py:1`), so the rules can be tested without HTTP.

## How it fits
- **Callers:** `src/harbor/api/routes.py` imports it as `booking_service` (`routes.py:11`). It calls `create_booking` (`routes.py:42`), `get_booking_for_guest` (`routes.py:57`) and `cancel_booking` (`routes.py:63`).
- **Tests:** `tests/services/test_bookings.py:8` imports the same three functions. `tests/services/test_arrivals.py:7` uses `create_booking` to set up data.
- **Dependencies:**
  - `InMemoryStore` (`repositories/memory.py`): `get_room` (`:22`), `bookings_for_room` (`:34`), `add_booking` (`:25`), `get_booking` (`:31`), `update_booking` (`:28`).
  - Domain types `Booking` and `BookingStatus` from `models.py`.
  - The domain errors from `errors.py`.
- **Flow:** route → service → store. Each function takes `store` explicitly. `today` is passed in by the route, which gets it from the `get_today` dependency (`routes.py:26`), so tests can freeze it. `main.py` turns the raised errors into 404, 422 or 409.

## Key parts
- **`create_booking`** (`bookings.py:19`): validates in a fixed order, checks for overlaps, computes the total and saves a `CONFIRMED` booking with a `uuid4().hex` id.
  - Order: the room exists, then `check_in` is not in the past, then `check_out` is after `check_in`, then the stay is at most 30 nights, then the guest count fits the room.
  - Total: `nights * room.nightly_rate_minor`, in integer minor units (`:57`).
- **`_overlaps`** (`:15`): treats stays as half-open ranges, so a check-out on the same day as another check-in is not a clash.
- **`get_booking_for_guest`** (`:63`): returns a different guest's booking as `NotFoundError`, not a 403. This follows the CLAUDE.md rule.
- **`cancel_booking`** (`:71`): looks the booking up through `get_booking_for_guest`, so ownership is enforced first. It then requires `CONFIRMED` status and at least `CANCEL_NOTICE_DAYS` before check-in. It saves a copy with status `CANCELLED` and `refund_minor` equal to `total_minor` (`:82`).
- **Constants** (`:11-12`): `MAX_NIGHTS = 30` and `CANCEL_NOTICE_DAYS = 2`.

## Gotchas
- **Check order matters.** An unknown room gives a 404 before any date problem is reported. A past `check_in` is reported before `check_out <= check_in`.
- **Only confirmed bookings block a room** (`:43`). Cancelled bookings free their dates, and `test_cancelled_booking_frees_the_room_for_the_same_dates` covers that.
- **Cancellation notice** is `(check_in - today).days < 2`, so cancelling exactly 2 days out is allowed. A breach raises `ConflictError` (409), not a validation error. The boundary test is `test_cancel_booking_allowed_exactly_at_notice_boundary`.
- **The refund is always 100%** inside the window (`:81-82`). There is no partial-refund logic. The refund is only recorded on the booking; nothing here moves money.
- **No locking.** The overlap check and `add_booking` are separate steps (`:42-59`). That is fine for a single-threaded in-memory demo. Two concurrent requests could double-book once a real database or threads are involved. The code has no handling for this, and the swap to a database is only mentioned in CLAUDE.md.
- **Linear scan.** `bookings_for_room` returns every booking for the room, including cancelled ones, and each is checked in turn. This is fine at demo scale.
- **Past dates are rejected** by the service, not by the schema. Cancelling after check-in is covered by the notice rule, because the day difference is negative.
- **Unclear from this file:** I haven't read `routes.py` or `memory.py` in full. What `bookings_for_room` returns for an unknown room, and whether the routes add extra validation, I haven't checked.

## Where to start if you need to change it
- **Rules and limits:** open `create_booking` (`bookings.py:19`) or `cancel_booking` (`:71`), and the constants at `:11-12`.
- **Tests:** `tests/services/test_bookings.py`. It has 16 tests, including the overlap, back-to-back, notice-boundary, refund and failed-cancel cases.
- **Route behaviour:** `tests/api/test_bookings_api.py` covers the HTTP layer.
- **Public contract:** changing a status code or field means asking first, per CLAUDE.md.
