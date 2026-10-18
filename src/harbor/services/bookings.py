"""Booking rules. No framework imports: these functions are tested without HTTP."""

import uuid
from dataclasses import replace
from datetime import date

from harbor.errors import ConflictError, NotFoundError, ValidationError
from harbor.models import Booking, BookingStatus
from harbor.repositories.memory import InMemoryStore

MAX_NIGHTS = 30
CANCEL_NOTICE_DAYS = 2


def _overlaps(a_in: date, a_out: date, b_in: date, b_out: date) -> bool:
    return a_in < b_out and b_in < a_out


def create_booking(
    store: InMemoryStore,
    *,
    guest_id: str,
    room_number: str,
    check_in: date,
    check_out: date,
    guests: int,
    today: date,
) -> Booking:
    """Book a room for a guest, enforcing dates, capacity and availability."""
    room = store.get_room(room_number)
    if room is None:
        raise NotFoundError(f"Room {room_number} does not exist")
    if check_in < today:
        raise ValidationError("check_in cannot be in the past")
    if check_out <= check_in:
        raise ValidationError("check_out must be after check_in")
    if (check_out - check_in).days > MAX_NIGHTS:
        raise ValidationError(f"Bookings are limited to {MAX_NIGHTS} nights")
    if guests < 1 or guests > room.capacity:
        raise ValidationError(f"Room {room_number} sleeps 1 to {room.capacity} guests")

    for existing in store.bookings_for_room(room_number):
        if existing.status is BookingStatus.CONFIRMED and _overlaps(
            check_in, check_out, existing.check_in, existing.check_out
        ):
            raise ConflictError(f"Room {room_number} is already booked for those dates")

    nights = (check_out - check_in).days
    booking = Booking(
        id=uuid.uuid4().hex,
        guest_id=guest_id,
        room_number=room_number,
        check_in=check_in,
        check_out=check_out,
        guests=guests,
        status=BookingStatus.CONFIRMED,
        total_minor=nights * room.nightly_rate_minor,
    )
    store.add_booking(booking)
    return booking


def get_booking_for_guest(store: InMemoryStore, *, booking_id: str, guest_id: str) -> Booking:
    """Return a booking only to the guest who owns it."""
    booking = store.get_booking(booking_id)
    if booking is None or booking.guest_id != guest_id:
        raise NotFoundError("Booking not found")
    return booking


def cancel_booking(store: InMemoryStore, *, booking_id: str, guest_id: str, today: date) -> Booking:
    """Cancel a confirmed booking at least CANCEL_NOTICE_DAYS before check-in."""
    booking = get_booking_for_guest(store, booking_id=booking_id, guest_id=guest_id)
    if booking.status is not BookingStatus.CONFIRMED:
        raise ConflictError("Only confirmed bookings can be cancelled")
    if (booking.check_in - today).days < CANCEL_NOTICE_DAYS:
        raise ConflictError(
            f"Bookings can only be cancelled at least {CANCEL_NOTICE_DAYS} days before check-in"
        )

    # Refund policy: a cancellation inside the allowed window refunds the full total.
    cancelled = replace(booking, status=BookingStatus.CANCELLED, refund_minor=booking.total_minor)
    store.update_booking(cancelled)
    return cancelled
