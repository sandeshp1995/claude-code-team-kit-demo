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


def test_cancel_booking_returns_cancelled_booking(client: TestClient) -> None:
    created = client.post("/bookings", json=NEW_BOOKING, headers=ALICE).json()

    response = client.post(f"/bookings/{created['id']}/cancel", headers=ALICE)

    assert response.status_code == 200
    assert response.json()["status"] == "cancelled"


def test_cancel_booking_refunds_the_full_total(client: TestClient) -> None:
    created = client.post("/bookings", json=NEW_BOOKING, headers=ALICE).json()

    response = client.post(f"/bookings/{created['id']}/cancel", headers=ALICE)

    assert response.json()["refund_minor"] == 24_000


def test_confirmed_booking_has_no_refund(client: TestClient) -> None:
    created = client.post("/bookings", json=NEW_BOOKING, headers=ALICE).json()

    response = client.get(f"/bookings/{created['id']}", headers=ALICE)

    assert response.json()["refund_minor"] is None


def test_cancel_booking_requires_auth(client: TestClient) -> None:
    created = client.post("/bookings", json=NEW_BOOKING, headers=ALICE).json()

    response = client.post(f"/bookings/{created['id']}/cancel")

    assert response.status_code == 401


def test_other_guest_gets_404_when_cancelling_booking(client: TestClient) -> None:
    created = client.post("/bookings", json=NEW_BOOKING, headers=ALICE).json()

    response = client.post(f"/bookings/{created['id']}/cancel", headers=BOB)

    assert response.status_code == 404
    assert client.get(f"/bookings/{created['id']}", headers=ALICE).json()["status"] == "confirmed"


def test_cancel_unknown_booking_returns_404(client: TestClient) -> None:
    response = client.post("/bookings/nope/cancel", headers=ALICE)

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "not_found"


def test_cancel_inside_notice_window_returns_409(client: TestClient) -> None:
    late = {**NEW_BOOKING, "check_in": "2026-11-03", "check_out": "2026-11-05"}
    created = client.post("/bookings", json=late, headers=ALICE).json()

    response = client.post(f"/bookings/{created['id']}/cancel", headers=ALICE)

    assert response.status_code == 409
    assert response.json()["error"]["code"] == "conflict"


def test_cancel_twice_returns_409(client: TestClient) -> None:
    created = client.post("/bookings", json=NEW_BOOKING, headers=ALICE).json()
    client.post(f"/bookings/{created['id']}/cancel", headers=ALICE)

    response = client.post(f"/bookings/{created['id']}/cancel", headers=ALICE)

    assert response.status_code == 409
