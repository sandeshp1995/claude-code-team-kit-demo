"""Demo authentication: a bearer token per guest, plus one front-desk staff token.

Real deployments would verify a signed token from the identity provider. The demo keeps a
static token table so the API can be tried without any setup.
"""

import hmac
from typing import Annotated

from fastapi import Depends, Header, HTTPException, status

DEMO_TOKENS = {
    "demo-token-alice": "guest-alice",
    "demo-token-bob": "guest-bob",
    "demo-token-staff": "staff-frontdesk",
}

STAFF_IDS = frozenset({"staff-frontdesk"})


def current_guest(authorization: Annotated[str | None, Header()] = None) -> str:
    """Resolve the bearer token to a caller id, or raise 401."""
    if authorization is None or not authorization.startswith("Bearer "):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Missing bearer token")
    supplied = authorization.removeprefix("Bearer ")
    for token, guest_id in DEMO_TOKENS.items():
        if hmac.compare_digest(token, supplied):
            return guest_id
    raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid token")


def current_staff(caller: Annotated[str, Depends(current_guest)]) -> str:
    """Resolve the caller and require a staff identity: 401 without a token, 403 for guests."""
    if caller not in STAFF_IDS:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Staff access required")
    return caller
