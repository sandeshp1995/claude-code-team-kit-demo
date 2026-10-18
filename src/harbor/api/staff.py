"""Front-desk endpoints. Staff only."""

import logging
from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends

from harbor.api.routes import Store
from harbor.api.schemas import ArrivalOut
from harbor.auth import current_staff
from harbor.services import arrivals as arrivals_service

logger = logging.getLogger(__name__)

router = APIRouter()

Staff = Annotated[str, Depends(current_staff)]


@router.get("/staff/arrivals", response_model=list[ArrivalOut])
def arrivals(day: date, _staff: Staff, store: Store) -> list[ArrivalOut]:
    """List the arrivals for a day, ordered by room number."""
    logger.info("arrivals requested for %s", day)
    return [ArrivalOut.from_domain(a) for a in arrivals_service.arrivals_on(store, day)]
