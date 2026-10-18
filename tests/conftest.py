from datetime import date

import pytest
from fastapi.testclient import TestClient

from harbor.api.routes import get_today
from harbor.main import create_app
from harbor.repositories.memory import InMemoryStore

TODAY = date(2026, 11, 2)
ALICE = {"Authorization": "Bearer demo-token-alice"}
BOB = {"Authorization": "Bearer demo-token-bob"}


@pytest.fixture
def store() -> InMemoryStore:
    return InMemoryStore()


@pytest.fixture
def client(store: InMemoryStore) -> TestClient:
    app = create_app(store)
    app.dependency_overrides[get_today] = lambda: TODAY
    return TestClient(app)
