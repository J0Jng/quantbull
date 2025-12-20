from typing import Generic, Optional, TypeVar
from pydantic.generics import GenericModel

T = TypeVar("T")


class ApiResponse(GenericModel, Generic[T]):
    code: int = 0
    message: str = "ok"
    data: Optional[T] = None


def success(data=None, message: str = "ok") -> dict:
    return ApiResponse(code=0, message=message, data=data).model_dump()


def error(message: str, code: int = 40001) -> dict:
    return ApiResponse(code=code, message=message, data=None).model_dump()
