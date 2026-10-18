"""Application factory and the single place domain errors become HTTP responses."""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from harbor.api.routes import router
from harbor.errors import ConflictError, HarborError, NotFoundError, ValidationError
from harbor.repositories.memory import InMemoryStore

_STATUS_FOR_ERROR: dict[type[HarborError], int] = {
    NotFoundError: 404,
    ValidationError: 422,
    ConflictError: 409,
}


def create_app(store: InMemoryStore | None = None) -> FastAPI:
    app = FastAPI(title="Harbor Hotel API", version="0.1.0")
    app.state.store = store or InMemoryStore()
    app.include_router(router)

    @app.exception_handler(HarborError)
    async def handle_domain_error(_: Request, exc: HarborError) -> JSONResponse:
        status_code = _STATUS_FOR_ERROR.get(type(exc), 400)
        return JSONResponse(
            status_code=status_code,
            content={"error": {"code": exc.code, "message": str(exc)}},
        )

    return app


app = create_app()
