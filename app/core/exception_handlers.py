from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
import traceback


async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    if isinstance(exc.detail, dict) and "code" in exc.detail:
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "code": exc.detail["code"],
                "message": exc.detail.get("message", str(exc.detail)),
                "data": exc.detail.get("data", None),
            },
        )
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "code": exc.status_code * 100 if exc.status_code < 500 else 50000,
            "message": str(exc.detail) if isinstance(exc.detail, str) else str(exc.detail),
            "data": None,
        },
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "code": 40001,
            "message": "参数校验失败",
            "data": None,
        },
    )


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    traceback.print_exc()
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "code": 50000,
            "message": "服务器内部错误，请稍后重试",
            "data": None,
        },
    )
