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
        """计算因子值（真实实现，基于 indicator_engine）"""
        with get_session() as session:
            factor = session.get(Factor, request.factor_id)
            if not factor:
                raise ValueError(f"因子不存在: {request.factor_id}")

        logger.info(
            "计算因子: %s (expression=%s), 标的: %s, %s - %s",
            factor.name,
            factor.expression,
            request.symbol,
            request.start_date,
            request.end_date,
        )

        values = await self._real_factor_calculation(
            expression=factor.expression,
            symbol=request.symbol,
            start_date=request.start_date,
            end_date=request.end_date,
            parameters=request.parameters or factor.parameters,
        )

        return FactorCalculateResponse(
            factor_id=request.factor_id,
            symbol=request.symbol,
            start_date=request.start_date,
            end_date=request.end_date,
            values=values,
            total_points=len(values),
        )

    async def _real_factor_calculation(
        self,
        expression: str,
        symbol: str,
        start_date: str,
        end_date: str,
        parameters: dict = None,
    ) -> list[dict]:
        """真实因子计算（基于 indicator_engine）"""
        from services.data_loader import load_market_data
        from services.indicator_engine import calculate_indicators, get_indicator_value

        # 1. 加载行情数据（多拉一段历史用于指标预热）
        from datetime import datetime, timedelta
        
        start_dt = datetime.strptime(start_date, "%Y-%m-%d")
        # 多拉 300 个交易日用于指标计算预热
        warmup_start = (start_dt - timedelta(days=450)).strftime("%Y-%m-%d")
        
        try:
            df = load_market_data(
                stock_code=symbol,
                start_date=warmup_start,
                end_date=end_date,
                source="tushare"
            )
        except Exception as e:
            logger.error(f"加载行情数据失败: {e}")
            raise ValueError(f"加载行情数据失败: {e}")

        if df.empty:
            raise ValueError(f"未获取到行情数据: {symbol}")

        logger.info(f"加载行情数据成功: {len(df)} 条记录")

        # 2. 计算技术指标
        try:
            indicator_df = calculate_indicators(df, end_date=end_date, threshold=300)
        except Exception as e:
            logger.error(f"计算技术指标失败: {e}")
            raise ValueError(f"计算技术指标失败: {e}")

        # 3. 根据表达式获取因子值
        try:
            factor_series = get_indicator_value(
                indicator_df,
                expression=expression,
                start_date=start_date,
                end_date=end_date,
            )
        except Exception as e:
            logger.error(f"获取因子值失败: {e}")
            raise ValueError(f"获取因子值失败: {e}")

        # 4. 转换为返回格式
        values = []
        for date_str, value in factor_series.items():
            values.append({
                "date": str(date_str),
                "value": round(float(value), 6) if not (value != value) else 0.0  # NaN check
            })

        logger.info(f"因子计算完成: {len(values)} 个数据点")
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
