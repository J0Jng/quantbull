from typing import Generic, Optional, TypeVar
from pydantic import BaseModel
from pydantic.generics import GenericModel

T = TypeVar("T")


class ApiResponse(BaseModel, Generic[T]):
    success: bool = True
    message: str = "ok"
    data: Optional[T] = None


def success(data=None, message: str = "ok") -> dict:
    return ApiResponse(success=True, message=message, data=data).model_dump()


def error(message: str, code: int = 40001) -> dict:
    return ApiResponse(success=False, message=message, data=None).model_dump()
