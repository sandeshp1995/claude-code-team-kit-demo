from fastapi.testclient import TestClient

from tests.conftest import ALICE


def test_arrivals(client: TestClient) -> None:
    client.post(
        "/bookings",
        json={"room_number": "101", "check_in": "2026-11-10", "check_out": "2026-11-11", "guests": 1},
        headers=ALICE,
    )
    response = client.get("/staff/arrivals?day=2026-11-10", headers=ALICE)
    assert response.status_code == 200
    assert len(response.json()) == 1
