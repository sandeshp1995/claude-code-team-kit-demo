from dataclasses import replace
from datetime import date

from harbor.models import BookingStatus
from harbor.repositories.memory import InMemoryStore
from harbor.services.arrivals import arrivals_on
from harbor.services.bookings import create_booking

TODAY = date(2026, 11, 2)
ARRIVAL_DAY = date(2026, 11, 10)


def book(store: InMemoryStore, room_number: str, check_in: date = ARRIVAL_DAY) -> str:
    booking = create_booking(
        store,
        guest_id="guest-alice",
        room_number=room_number,
        check_in=check_in,
        check_out=date(2026, 11, 12),
        guests=1,
        today=TODAY,
    )
    return booking.id


def test_arrivals_are_sorted_by_room_number(store: InMemoryStore) -> None:
    book(store, "201")
    book(store, "101")
    book(store, "102")

    result = arrivals_on(store, ARRIVAL_DAY)

    assert [a.room_number for a in result] == ["101", "102", "201"]


def test_arrivals_exclude_cancelled_bookings(store: InMemoryStore) -> None:
    kept = book(store, "101")
    cancelled_id = book(store, "102")
    cancelled = store.get_booking(cancelled_id)
    assert cancelled is not None
    store.update_booking(replace(cancelled, status=BookingStatus.CANCELLED))

    result = arrivals_on(store, ARRIVAL_DAY)

    assert [a.booking_id for a in result] == [kept]


def test_arrivals_exclude_other_days(store: InMemoryStore) -> None:
    book(store, "101", check_in=date(2026, 11, 11))

    result = arrivals_on(store, ARRIVAL_DAY)

    assert result == []


def test_arrival_carries_room_kind_and_integer_total(store: InMemoryStore) -> None:
    book(store, "102")

    (arrival,) = arrivals_on(store, ARRIVAL_DAY)

    assert arrival.room_kind == "double"
    assert arrival.nights == 2
    assert arrival.total_minor == 24_000
