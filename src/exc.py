from fastapi import FastAPI, Request, status, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException


# --- Custom Exception Classes ---
class StringAlreadyExistsException(HTTPException):
    pass

class StringNotFoundException(HTTPException):
    pass

class UnparsableNaturalLanguageException(HTTPException):
    pass

class InternalSystemError(HTTPException):  # renamed from SystemError
    pass


# --- Helper ---
async def exc_handler(status_code: int, content: dict):
    return JSONResponse(status_code=status_code, content=content)


# --- Handlers ---
async def natural_language(request: Request, exc: UnparsableNaturalLanguageException):
    return await exc_handler(
        exc.status_code,
        {"error": "Unable to parse content", "detail": exc.detail},
    )

async def system_error(request: Request, exc: InternalSystemError):
    return await exc_handler(
        exc.status_code,
        {"error": "System Unable to Process the request", "detail": exc.detail},
    )

async def string_already_exists(request: Request, exc: StringAlreadyExistsException):
    return await exc_handler(
        exc.status_code,
        {"error": "String Already Exists", "detail": exc.detail},
    )

async def string_not_found(request: Request, exc: StringNotFoundException):
    return await exc_handler(
        exc.status_code,
        {"error": "String Not Found", "detail": exc.detail},
    )


async def request_validation(request: Request, exc: RequestValidationError):
    errors = exc.errors()

    # Missing field → 400
    if any("missing" in err["type"] for err in errors):
        return await exc_handler(
            status.HTTP_400_BAD_REQUEST,
            {"error": "Invalid request body or missing 'value' field"},
        )

    # Wrong type → 422
    if any(
        err["type"] in ["string_type", "str_type", "type_error", "value_error"]
        for err in errors
    ):
        return await exc_handler(
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            {"error": "Invalid data type for 'value' (must be string)"},
        )

    # Fallback
    return await exc_handler(
        status.HTTP_422_UNPROCESSABLE_ENTITY,
        {"error": "Unprocessable entity", "detail": errors},
    )


async def starlette_validation(request: Request, exc: StarletteHTTPException):
    detail_str = str(exc.detail).lower() if exc.detail else ""

    if any(
        phrase in detail_str
        for phrase in [
            "malformed",
            "json",
            "body",
            "parse error",
            "invalid json",
        ]
    ):
        return await exc_handler(
            status.HTTP_400_BAD_REQUEST,
            {"error": "Malformed or invalid JSON body"},
        )

    return await exc_handler(
        exc.status_code,
        {"error": str(exc.detail) or "Unexpected parsing error"},
    )


# --- Registration ---
def register_exc(app: FastAPI):
    app.add_exception_handler(StringAlreadyExistsException, string_already_exists)
    app.add_exception_handler(StringNotFoundException, string_not_found)
    app.add_exception_handler(UnparsableNaturalLanguageException, natural_language)
    app.add_exception_handler(RequestValidationError, request_validation)
    app.add_exception_handler(StarletteHTTPException, starlette_validation)
    app.add_exception_handler(InternalSystemError, system_error)
