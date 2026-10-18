"""Request and response bodies. ORM/domain objects are never returned directly."""

from datetime import date

from pydantic import BaseModel, Field

from harbor.models import Booking, BookingStatus, Room


class RoomOut(BaseModel):
    number: str
    kind: str
    nightly_rate_minor: int
    currency: str = "USD"
    capacity: int

    @classmethod
    def from_domain(cls, room: Room) -> "RoomOut":
        return cls(
            number=room.number,
            kind=room.kind,
            nightly_rate_minor=room.nightly_rate_minor,
            capacity=room.capacity,
        )


class BookingIn(BaseModel):
    room_number: str = Field(min_length=1, max_length=10)
    check_in: date
    check_out: date
    guests: int = Field(ge=1, le=10)


class BookingOut(BaseModel):
    id: str
    room_number: str
    check_in: date
    check_out: date
    nights: int
    guests: int
    status: str
    total_minor: int
    currency: str = "USD"
    refund_minor: int | None = None

    @classmethod
    def from_domain(cls, booking: Booking) -> "BookingOut":
        return cls(
            id=booking.id,
            room_number=booking.room_number,
            check_in=booking.check_in,
            check_out=booking.check_out,
            nights=booking.nights,
            guests=booking.guests,
            status=booking.status.value,
            total_minor=booking.total_minor,
            refund_minor=(
                booking.total_minor if booking.status is BookingStatus.CANCELLED else None
            ),
        )
