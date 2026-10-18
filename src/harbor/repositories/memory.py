"""In-memory storage. Swappable for a database-backed repository later."""

from harbor.models import Booking, Room

SEED_ROOMS = (
    Room(number="101", kind="single", nightly_rate_minor=9_000, capacity=1),
    Room(number="102", kind="double", nightly_rate_minor=12_000, capacity=2),
    Room(number="201", kind="suite", nightly_rate_minor=25_000, capacity=4),
)


class InMemoryStore:
    def __init__(self, rooms: tuple[Room, ...] = SEED_ROOMS) -> None:
        self._rooms = {room.number: room for room in rooms}
        self._bookings: dict[str, Booking] = {}

    def list_rooms(self) -> list[Room]:
        return sorted(self._rooms.values(), key=lambda room: room.number)

    def get_room(self, number: str) -> Room | None:
        return self._rooms.get(number)

    def add_booking(self, booking: Booking) -> None:
        self._bookings[booking.id] = booking

    def get_booking(self, booking_id: str) -> Booking | None:
        return self._bookings.get(booking_id)

    def bookings_for_room(self, room_number: str) -> list[Booking]:
        return [b for b in self._bookings.values() if b.room_number == room_number]
