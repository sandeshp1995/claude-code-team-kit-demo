"""Domain types shared by the service and API layers."""

from dataclasses import dataclass
from datetime import date
from enum import StrEnum


class BookingStatus(StrEnum):
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"


@dataclass(frozen=True)
class Room:
    number: str
    kind: str
    nightly_rate_minor: int
    capacity: int


@dataclass
class Booking:
    id: str
    guest_id: str
    room_number: str
    check_in: date
    check_out: date
    guests: int
    status: BookingStatus
    total_minor: int

    @property
    def nights(self) -> int:
        return (self.check_out - self.check_in).days
