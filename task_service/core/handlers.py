from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError, HTTPException as StarletteHTTPException
from .response import ApiResponse


async def http_exception_handler(request: Request, exc: Exception):
    if isinstance(exc, StarletteHTTPException):
        status = exc.status_code or 400
        detail = getattr(exc, "detail", str(exc))
    else:
        status = 500
        detail = str(exc)
    payload = ApiResponse(code=status, message=str(detail), data=None).model_dump()
    return JSONResponse(status_code=status, content=payload)


async def validation_exception_handler(request: Request, exc: Exception):
    if isinstance(exc, RequestValidationError):
        try:
            errors = exc.errors()
            msgs = [e.get("msg", "") for e in errors]
            msg = "; ".join(msgs)
        except Exception:
            msg = str(exc)
        payload = ApiResponse(code=422, message=msg, data=None).model_dump()
        return JSONResponse(status_code=422, content=payload)

    payload = ApiResponse(code=500, message=str(exc), data=None).model_dump()
    return JSONResponse(status_code=500, content=payload)


async def generic_exception_handler(request: Request, exc: Exception):
    payload = ApiResponse(code=500, message="internal server error", data=None).model_dump()
    return JSONResponse(status_code=500, content=payload)
