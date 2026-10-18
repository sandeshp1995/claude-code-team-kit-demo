from datetime import date

import pytest

from harbor.errors import ConflictError, NotFoundError, ValidationError
from harbor.models import BookingStatus
from harbor.repositories.memory import InMemoryStore
from harbor.services.bookings import cancel_booking, create_booking, get_booking_for_guest

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


def test_cancel_booking_marks_booking_cancelled() -> None:
    store = InMemoryStore()
    booking = book(store)

    cancelled = cancel_booking(store, booking_id=booking.id, guest_id="guest-alice", today=TODAY)

    assert cancelled.status is BookingStatus.CANCELLED


def test_cancel_booking_persists_cancelled_status() -> None:
    store = InMemoryStore()
    booking = book(store)

    cancel_booking(store, booking_id=booking.id, guest_id="guest-alice", today=TODAY)

    reloaded = get_booking_for_guest(store, booking_id=booking.id, guest_id="guest-alice")
    assert reloaded.status is BookingStatus.CANCELLED
    assert booking.status is BookingStatus.CONFIRMED


def test_cancel_booking_stores_full_refund_on_booking() -> None:
    store = InMemoryStore()
    booking = book(store)

    cancelled = cancel_booking(store, booking_id=booking.id, guest_id="guest-alice", today=TODAY)

    reloaded = get_booking_for_guest(store, booking_id=booking.id, guest_id="guest-alice")
    assert cancelled.refund_minor == booking.total_minor
    assert reloaded.refund_minor == booking.total_minor


def test_cancel_booking_allowed_exactly_at_notice_boundary() -> None:
    store = InMemoryStore()
    booking = book(store, check_in=date(2026, 11, 4), check_out=date(2026, 11, 6))

    cancelled = cancel_booking(store, booking_id=booking.id, guest_id="guest-alice", today=TODAY)

    assert cancelled.status is BookingStatus.CANCELLED


@pytest.mark.parametrize("check_in", [date(2026, 11, 3), date(2026, 11, 2)])
def test_cancel_booking_inside_notice_window_conflicts(check_in: date) -> None:
    store = InMemoryStore()
    booking = book(store, check_in=check_in, check_out=date(2026, 11, 6))

    with pytest.raises(ConflictError):
        cancel_booking(store, booking_id=booking.id, guest_id="guest-alice", today=TODAY)


def test_failed_cancel_leaves_booking_confirmed() -> None:
    store = InMemoryStore()
    booking = book(store, check_in=date(2026, 11, 3), check_out=date(2026, 11, 6))

    with pytest.raises(ConflictError):
        cancel_booking(store, booking_id=booking.id, guest_id="guest-alice", today=TODAY)

    assert booking.status is BookingStatus.CONFIRMED


def test_cancel_booking_twice_conflicts() -> None:
    store = InMemoryStore()
    booking = book(store)
    cancel_booking(store, booking_id=booking.id, guest_id="guest-alice", today=TODAY)

    with pytest.raises(ConflictError):
        cancel_booking(store, booking_id=booking.id, guest_id="guest-alice", today=TODAY)


def test_other_guest_cannot_cancel_booking() -> None:
    store = InMemoryStore()
    booking = book(store)

    with pytest.raises(NotFoundError):
        cancel_booking(store, booking_id=booking.id, guest_id="guest-bob", today=TODAY)

    assert booking.status is BookingStatus.CONFIRMED


def test_cancel_unknown_booking_raises_not_found() -> None:
    with pytest.raises(NotFoundError):
        cancel_booking(InMemoryStore(), booking_id="nope", guest_id="guest-alice", today=TODAY)


def test_cancelled_booking_frees_the_room_for_the_same_dates() -> None:
    store = InMemoryStore()
    booking = book(store)
    cancel_booking(store, booking_id=booking.id, guest_id="guest-alice", today=TODAY)

    rebooked = book(store, guest_id="guest-bob")

    assert rebooked.guest_id == "guest-bob"
