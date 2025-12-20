from typing import Generic, List, Optional, TypeVar

from pydantic import BaseModel
from pydantic.generics import GenericModel

from .backtest import BacktestResponse

T = TypeVar("T")


class BaseResponse(GenericModel, Generic[T]):
    """统一响应信封

    包含通用字段：success, data, message
    """
    success: bool
    data: Optional[T] = None
    message: Optional[str] = None


class PaginatedResponse(GenericModel, Generic[T]):
    """分页响应信封

    字段：total, items
    """
    total: int
    items: List[T]


# BacktestDetail 复用现有的 BacktestResponse 结构以保持向后兼容
BacktestDetail = BacktestResponse
