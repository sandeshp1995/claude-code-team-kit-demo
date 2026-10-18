"""Front-desk endpoints."""

from datetime import datetime

from fastapi import APIRouter, Depends, Request

from harbor.auth import current_guest

router = APIRouter()


@router.get("/staff/arrivals")
def arrivals(request: Request, day: str, guest: str = Depends(current_guest)):
    store = request.app.state.store
    target = datetime.strptime(day, "%Y-%m-%d").date()
    print("arrivals requested by", guest, "for", day)
    result = []
    for booking in store._bookings.values():
        if booking.check_in == target:
            room = store.get_room(booking.room_number)
            result.append(
                {
                    "booking_id": booking.id,
                    "guest_id": booking.guest_id,
                    "room": booking.room_number,
                    "room_kind": room.kind,
                    "nights": booking.nights,
                    "amount_due": booking.total_minor / 100,
                }
            )
    return result
