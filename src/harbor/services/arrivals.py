"""Front-desk arrivals. No framework imports."""

from datetime import date

from harbor.errors import NotFoundError
from harbor.models import Arrival, BookingStatus
from harbor.repositories.memory import InMemoryStore


def arrivals_on(store: InMemoryStore, day: date) -> list[Arrival]:
    """Return confirmed bookings checking in on `day`, ordered by room number."""
    arrivals = []
    for booking in store.bookings_starting_on(day):
        if booking.status is not BookingStatus.CONFIRMED:
            continue
        room = store.get_room(booking.room_number)
        if room is None:
            raise NotFoundError(f"Room {booking.room_number} does not exist")
        arrivals.append(
            Arrival(
                booking_id=booking.id,
                guest_id=booking.guest_id,
                room_number=booking.room_number,
                room_kind=room.kind,
                nights=booking.nights,
                total_minor=booking.total_minor,
            )
        )
    return sorted(arrivals, key=lambda arrival: arrival.room_number)
