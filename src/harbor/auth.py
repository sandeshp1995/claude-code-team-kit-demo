"""Demo authentication: a bearer token per guest.

Real deployments would verify a signed token from the identity provider. The demo keeps a
static token table so the API can be tried without any setup.
"""

import hmac
from typing import Annotated

from fastapi import Header, HTTPException, status

DEMO_TOKENS = {
    "demo-token-alice": "guest-alice",
    "demo-token-bob": "guest-bob",
}


def current_guest(authorization: Annotated[str | None, Header()] = None) -> str:
    if authorization is None or not authorization.startswith("Bearer "):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Missing bearer token")
    supplied = authorization.removeprefix("Bearer ")
    for token, guest_id in DEMO_TOKENS.items():
        if hmac.compare_digest(token, supplied):
            return guest_id
    raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid token")
