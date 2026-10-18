from fastapi.testclient import TestClient

from tests.conftest import ALICE, BOB, STAFF

ARRIVALS_URL = "/staff/arrivals?day=2026-11-10"


def book(client: TestClient, room_number: str, check_in: str = "2026-11-10") -> None:
    response = client.post(
        "/bookings",
        json={
            "room_number": room_number,
            "check_in": check_in,
            "check_out": "2026-11-12",
            "guests": 1,
        },
        headers=ALICE,
    )
    assert response.status_code == 201


def test_staff_sees_arrivals_for_the_day_ordered_by_room(client: TestClient) -> None:
    book(client, "201")
    book(client, "101")

    response = client.get(ARRIVALS_URL, headers=STAFF)

    assert response.status_code == 200
    assert [a["room"] for a in response.json()] == ["101", "201"]
    assert response.json()[0]["guest_id"] == "guest-alice"
    assert response.json()[0]["room_kind"] == "single"


def test_arrival_amount_is_integer_minor_units_with_currency(client: TestClient) -> None:
    book(client, "101")

    body = client.get(ARRIVALS_URL, headers=STAFF).json()[0]

    assert body["total_minor"] == 18_000
    assert isinstance(body["total_minor"], int)
    assert body["currency"] == "USD"
    assert "amount_due" not in body


def test_arrivals_exclude_bookings_starting_on_other_days(client: TestClient) -> None:
    book(client, "101", check_in="2026-11-11")

    response = client.get(ARRIVALS_URL, headers=STAFF)

    assert response.json() == []


def test_arrivals_exclude_cancelled_bookings(client: TestClient) -> None:
    book(client, "101")
    booking_id = client.get(ARRIVALS_URL, headers=STAFF).json()[0]["booking_id"]
    client.post(f"/bookings/{booking_id}/cancel", headers=ALICE)

    response = client.get(ARRIVALS_URL, headers=STAFF)

    assert response.json() == []


def test_arrivals_with_bad_date_returns_422(client: TestClient) -> None:
    response = client.get("/staff/arrivals?day=garbage", headers=STAFF)

    assert response.status_code == 422


def test_arrivals_without_day_returns_422(client: TestClient) -> None:
    response = client.get("/staff/arrivals", headers=STAFF)

    assert response.status_code == 422


def test_arrivals_require_a_token(client: TestClient) -> None:
    response = client.get(ARRIVALS_URL)

    assert response.status_code == 401


def test_arrivals_reject_an_unknown_token(client: TestClient) -> None:
    response = client.get(ARRIVALS_URL, headers={"Authorization": "Bearer nope"})

    assert response.status_code == 401


def test_guest_gets_403_on_arrivals(client: TestClient) -> None:
    book(client, "101")

    response = client.get(ARRIVALS_URL, headers=BOB)

    assert response.status_code == 403
    assert "guest-alice" not in response.text
