# Changelog

Release notes are generated with `/release-notes` from the Claude Code Team Kit, then checked by a human. "Needs a human check" items are kept so you can see what the command flags.

## v0.2.0, 2026-10-19

Range: `dc860a5..HEAD` (6 commits). Audience: internal.

### Breaking changes
- None found. `GET /staff/arrivals` is new in this range, so no earlier contract changed. `amount_due` (a float) was replaced by `total_minor` and `currency`, but that only affects the first draft of the endpoint, not a released API.

### New features
- Add `POST /bookings/{booking_id}/cancel`. A guest can cancel their own confirmed booking at least 2 days before check-in. A late or repeat cancel returns 409, and another guest's booking returns 404. Cancelling frees the room for those dates. HB-3
- Add a `refund_minor` field to booking responses. It holds the full total for cancelled bookings and is null otherwise. HB-3
- Add the front-desk `GET /staff/arrivals?day=YYYY-MM-DD` endpoint, which lists arrivals for a day ordered by room number. It is staff-only and uses a new `demo-token-staff` demo token. HB-5

### Improvements
- Reword the late-cancellation error to state the notice period in days. HB-3
- Return arrival amounts as `total_minor` plus `currency` instead of a float `amount_due`, per the money convention. HB-5

### Bug fixes
- Fix cancellations relying on in-memory object aliasing for persistence. They are now saved through `InMemoryStore.update_booking`, so they will work with a real database. HB-3
- Remove the stray `.venv` symlink committed in #2, which broke the environment for anyone cloning the repo, and ignore `.venv` as a file or folder.

### Internal
- Move the refund policy into the service layer, so the API schema only maps domain values.
- Rework the arrivals endpoint to follow project conventions: service layer, Pydantic schemas, `get_today`-style date typing, logging instead of `print`, and no reaching into private store state. Add service and API tests. HB-5
- Update docs to describe the deliberately rough demo PR accurately.

### Needs a human check
- `9d09421` ("add arrivals endpoint…") has no Conventional Commit prefix. I treated it as part of the HB-5 arrivals feature and merged it into that line.
- `c2023b9` is titled "wip: HB-5 review fixes (message to be replaced by /commit-msg)". Its message is still a placeholder. I classified it from the diff, and its subject should be rewritten before release.
- The staff-token addition in `auth.py` is a new public demo token. Confirm that's intended for the release, since `CLAUDE.md` currently lists only the alice and bob tokens.

## v0.1.0, 2026-10-18

- Rooms list, create a booking, read your own booking.
- Service-layer rules for dates, capacity and overlapping bookings; one domain-error mapping.
