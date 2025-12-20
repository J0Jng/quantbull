import json
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


async def envelope_middleware(request: Request, call_next):
    response = await call_next(request)
    content_type = response.headers.get("content-type", "")
    if "application/json" in content_type:
        try:
            body = b""
            async for chunk in response.body_iterator:
                body += chunk
            text = body.decode() if body else ""
            data = json.loads(text) if text else None
        except Exception:
            return response

        if isinstance(data, dict) and {"code", "message", "data"}.issubset(set(data.keys())):
            return JSONResponse(content=data, status_code=response.status_code, headers=dict(response.headers))
        enveloped = ApiResponse(code=0 if 200 <= response.status_code < 400 else response.status_code,
                                message="ok" if 200 <= response.status_code < 400 else "error",
                                data=data).model_dump()
        return JSONResponse(content=enveloped, status_code=response.status_code, headers=dict(response.headers))

    return response
