"""Domain exceptions. The API layer maps these to HTTP responses in one place."""


class HarborError(Exception):
    code = "harbor_error"


class NotFoundError(HarborError):
    code = "not_found"


class ValidationError(HarborError):
    code = "invalid_request"


class ConflictError(HarborError):
    code = "conflict"
