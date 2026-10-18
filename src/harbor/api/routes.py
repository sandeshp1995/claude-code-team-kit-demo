"""HTTP layer: validate input, call one service function, shape the response."""

from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, Request, Response, status

from harbor.api.schemas import BookingIn, BookingOut, RoomOut
from harbor.auth import current_guest
from harbor.repositories.memory import InMemoryStore
from harbor.services import bookings as booking_service

router = APIRouter()

Guest = Annotated[str, Depends(current_guest)]


def get_store(request: Request) -> InMemoryStore:
    store: InMemoryStore = request.app.state.store
    return store


Store = Annotated[InMemoryStore, Depends(get_store)]


def get_today() -> date:
    return date.today()


Today = Annotated[date, Depends(get_today)]


@router.get("/rooms", response_model=list[RoomOut])
def list_rooms(store: Store) -> list[RoomOut]:
    return [RoomOut.from_domain(room) for room in store.list_rooms()]


@router.post("/bookings", response_model=BookingOut, status_code=status.HTTP_201_CREATED)
def create_booking(
    body: BookingIn, guest: Guest, store: Store, today: Today, response: Response
) -> BookingOut:
    booking = booking_service.create_booking(
        store,
        guest_id=guest,
        room_number=body.room_number,
        check_in=body.check_in,
        check_out=body.check_out,
        guests=body.guests,
        today=today,
    )
    response.headers["Location"] = f"/bookings/{booking.id}"
    return BookingOut.from_domain(booking)


@router.get("/bookings/{booking_id}", response_model=BookingOut)
def get_booking(booking_id: str, guest: Guest, store: Store) -> BookingOut:
    booking = booking_service.get_booking_for_guest(store, booking_id=booking_id, guest_id=guest)
    return BookingOut.from_domain(booking)
