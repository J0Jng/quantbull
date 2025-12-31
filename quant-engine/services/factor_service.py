from datetime import date, timedelta
from typing import Optional

from sqlmodel import select

from core.logger import get_logger
from db import get_session
from models.factor import Factor
from schemas.factor import (
    ALLOWED_DATA_SOURCES,
    FactorCalculateRequest,
    FactorCalculateResponse,
    FactorCreateRequest,
    FactorResponse,
    FactorUpdateRequest,
)

logger = get_logger(__name__)


class FactorService:
    """因子服务，使用数据库持久化"""

    async def create_factor(self, request: FactorCreateRequest) -> FactorResponse:
        """创建因子"""
        if request.data_source not in ALLOWED_DATA_SOURCES:
            raise ValueError(f"data_source 必须是: {', '.join(ALLOWED_DATA_SOURCES)}")

        factor = Factor(
            name=request.name,
            description=request.description,
            expression=request.expression,
            data_source=request.data_source,
            category=request.category,
            formula=request.formula or request.expression,
            parameters=request.parameters,
        )

        with get_session() as session:
            session.add(factor)
            session.commit()
            session.refresh(factor)

        logger.info(f"创建因子: {factor.id} - {factor.name}")
        return self._to_response(factor)

    async def get_factor(self, factor_id: str) -> Optional[FactorResponse]:
        """获取因子"""
        with get_session() as session:
            factor = session.get(Factor, factor_id)
            if not factor:
                return None
            return self._to_response(factor)

    async def update_factor(self, factor_id: str, request: FactorUpdateRequest) -> Optional[FactorResponse]:
        """更新因子"""
        with get_session() as session:
            factor = session.get(Factor, factor_id)
            if not factor:
                return None

            update_data = request.model_dump(exclude_unset=True)
            if "data_source" in update_data and update_data["data_source"] not in ALLOWED_DATA_SOURCES:
                raise ValueError(f"data_source 必须是: {', '.join(ALLOWED_DATA_SOURCES)}")

            for key, value in update_data.items():
                if value is not None:
                    setattr(factor, key, value)

            session.add(factor)
            session.commit()
            session.refresh(factor)

            logger.info(f"更新因子: {factor_id}")
            return self._to_response(factor)

    async def delete_factor(self, factor_id: str) -> bool:
        """删除因子"""
        with get_session() as session:
            factor = session.get(Factor, factor_id)
            if not factor:
                return False
            session.delete(factor)
            session.commit()
            logger.info(f"删除因子: {factor_id}")
            return True

    async def list_factors(
        self,
        category: Optional[str] = None,
        limit: int = 20,
        offset: int = 0,
    ) -> tuple[list[FactorResponse], int]:
        """列出因子"""
        base_stmt = select(Factor)
        if category:
            base_stmt = base_stmt.where(Factor.category == category)

        data_stmt = base_stmt.offset(offset).limit(limit)

        with get_session() as session:
            factors = session.exec(data_stmt).all()
            total = session.exec(base_stmt).all()
            return [self._to_response(f) for f in factors], len(total)

    async def calculate_factor(self, request: FactorCalculateRequest) -> FactorCalculateResponse:
        """计算因子值（示例，仍为模拟实现）"""
        with get_session() as session:
            factor = session.get(Factor, request.factor_id)
            if not factor:
                raise ValueError(f"因子不存在: {request.factor_id}")

        logger.info(
            "计算因子: %s, 标的: %s, %s - %s",
            factor.name,
            request.symbol,
            request.start_date,
            request.end_date,
        )

        values = await self._simulate_factor_calculation(request)

        return FactorCalculateResponse(
            factor_id=request.factor_id,
            symbol=request.symbol,
            start_date=request.start_date,
            end_date=request.end_date,
            values=values,
            total_points=len(values),
        )

    async def _simulate_factor_calculation(self, request: FactorCalculateRequest) -> list[dict]:
        """模拟因子计算（示例实现）"""
        import random

        start = date.fromisoformat(request.start_date)
        end = date.fromisoformat(request.end_date)

        values = []
        current_date = start

        base_value = random.uniform(0, 100)
        while current_date <= end:
            change = random.uniform(-2.0, 2.0)
            base_value = max(0, min(100, base_value + change))
            values.append({"date": current_date.isoformat(), "value": round(base_value, 4)})
            current_date += timedelta(days=1)

        return values

    @staticmethod
    def _to_response(factor: Factor) -> FactorResponse:
        return FactorResponse(
            id=factor.id,
            name=factor.name,
            description=factor.description,
            expression=factor.expression,
            data_source=factor.data_source,
            category=factor.category,
            formula=factor.formula,
            parameters=factor.parameters or {},
            created_at=factor.created_at.isoformat(),
        )
