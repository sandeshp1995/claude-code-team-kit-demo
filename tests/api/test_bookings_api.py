from fastapi.testclient import TestClient

from tests.conftest import ALICE, BOB

NEW_BOOKING = {
    "room_number": "102",
    "check_in": "2026-11-10",
    "check_out": "2026-11-12",
    "guests": 2,
}


def test_list_rooms_is_public(client: TestClient) -> None:
    response = client.get("/rooms")

    assert response.status_code == 200
    assert [room["number"] for room in response.json()] == ["101", "102", "201"]


def test_create_booking_returns_201_with_location(client: TestClient) -> None:
    response = client.post("/bookings", json=NEW_BOOKING, headers=ALICE)

    assert response.status_code == 201
    assert response.headers["Location"] == f"/bookings/{response.json()['id']}"
    assert response.json()["total_minor"] == 24_000


def test_create_booking_requires_auth(client: TestClient) -> None:
    response = client.post("/bookings", json=NEW_BOOKING)

    assert response.status_code == 401


def test_double_booking_returns_409(client: TestClient) -> None:
    client.post("/bookings", json=NEW_BOOKING, headers=ALICE)

    response = client.post("/bookings", json=NEW_BOOKING, headers=BOB)

    assert response.status_code == 409
    assert response.json()["error"]["code"] == "conflict"


def test_owner_can_read_booking(client: TestClient) -> None:
    created = client.post("/bookings", json=NEW_BOOKING, headers=ALICE).json()

    response = client.get(f"/bookings/{created['id']}", headers=ALICE)

    assert response.status_code == 200
    assert response.json()["id"] == created["id"]


def test_other_guest_gets_404_for_booking(client: TestClient) -> None:
    created = client.post("/bookings", json=NEW_BOOKING, headers=ALICE).json()

    response = client.get(f"/bookings/{created['id']}", headers=BOB)

    assert response.status_code == 404
