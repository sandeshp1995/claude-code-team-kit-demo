from datetime import date

import pytest

from harbor.errors import ConflictError, NotFoundError, ValidationError
from harbor.repositories.memory import InMemoryStore
from harbor.services.bookings import create_booking, get_booking_for_guest

TODAY = date(2026, 11, 2)


def book(store: InMemoryStore, **overrides: object):  # type: ignore[no-untyped-def]
    params: dict[str, object] = {
        "guest_id": "guest-alice",
        "room_number": "102",
        "check_in": date(2026, 11, 10),
        "check_out": date(2026, 11, 12),
        "guests": 2,
        "today": TODAY,
    }
    params.update(overrides)
    return create_booking(store, **params)  # type: ignore[arg-type]


def test_create_booking_charges_nightly_rate_per_night() -> None:
    booking = book(InMemoryStore())

    assert booking.nights == 2
    assert booking.total_minor == 24_000


@pytest.mark.parametrize(
    ("overrides", "message"),
    [
        ({"check_in": date(2026, 11, 1)}, "past"),
        ({"check_out": date(2026, 11, 10)}, "after check_in"),
        ({"check_out": date(2026, 12, 15)}, "30 nights"),
        ({"guests": 3}, "sleeps 1 to 2"),
    ],
)
def test_create_booking_rejects_invalid_requests(
    overrides: dict[str, object], message: str
) -> None:
    with pytest.raises(ValidationError, match=message):
        book(InMemoryStore(), **overrides)


def test_create_booking_rejects_unknown_room() -> None:
    with pytest.raises(NotFoundError):
        book(InMemoryStore(), room_number="999")


def test_create_booking_rejects_overlapping_dates() -> None:
    store = InMemoryStore()
    book(store)

    with pytest.raises(ConflictError):
        book(store, guest_id="guest-bob", check_in=date(2026, 11, 11), check_out=date(2026, 11, 13))


def test_back_to_back_bookings_are_allowed() -> None:
    store = InMemoryStore()
    book(store)

    second = book(store, check_in=date(2026, 11, 12), check_out=date(2026, 11, 14))

    assert second.check_in == date(2026, 11, 12)


def test_guest_cannot_read_another_guests_booking() -> None:
    store = InMemoryStore()
    booking = book(store)

    with pytest.raises(NotFoundError):
        get_booking_for_guest(store, booking_id=booking.id, guest_id="guest-bob")
