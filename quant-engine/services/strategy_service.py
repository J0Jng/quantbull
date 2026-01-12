from datetime import datetime
from typing import Optional

from sqlmodel import select

from core.logger import get_logger
from db import get_session
from models.factor import Factor
from models.strategy import Strategy
from schemas.strategy import (
    ALLOWED_STATUSES,
    StrategyCreateRequest,
    StrategyResponse,
    StrategyUpdateRequest,
    StrategyValidateRequest,
    StrategyValidateResponse,
)
from services.strategy_loader import list_builtin_strategies

logger = get_logger(__name__)


class StrategyService:
    """策略服务，使用数据库持久化"""

    async def create_strategy(self, request: StrategyCreateRequest) -> StrategyResponse:
        """创建策略"""
        if not request.factor_ids:
            raise ValueError("factor_ids 不允许为空")
        if request.status not in ALLOWED_STATUSES:
            raise ValueError(f"status 必须是: {', '.join(ALLOWED_STATUSES)}")

        await self._assert_factors_exist(request.factor_ids)

        strategy = Strategy(
            name=request.name,
            description=request.description,
            code=request.code,
            factor_ids=request.factor_ids,
            parameters=request.parameters,
            status=request.status,
        )

        with get_session() as session:
            session.add(strategy)
            session.commit()
            session.refresh(strategy)

        logger.info("创建策略: %s - %s", strategy.id, strategy.name)
        return self._to_response(strategy)

    async def get_strategy(self, strategy_id: str) -> Optional[StrategyResponse]:
        """获取策略"""
        with get_session() as session:
            strategy = session.get(Strategy, strategy_id)
            if not strategy:
                return None
            return self._to_response(strategy)

    async def update_strategy(self, strategy_id: str, request: StrategyUpdateRequest) -> Optional[StrategyResponse]:
        """更新策略"""
        with get_session() as session:
            strategy = session.get(Strategy, strategy_id)
            if not strategy:
                return None

            update_data = request.model_dump(exclude_unset=True)

            if "factor_ids" in update_data:
                factor_ids = update_data["factor_ids"]
                if factor_ids is None or len(factor_ids) == 0:
                    raise ValueError("factor_ids 不允许为空")
                await self._assert_factors_exist(factor_ids)

            if "status" in update_data:
                status = update_data["status"]
                if status and status not in ALLOWED_STATUSES:
                    raise ValueError(f"status 必须是: {', '.join(ALLOWED_STATUSES)}")

            for key, value in update_data.items():
                if value is not None:
                    setattr(strategy, key, value)

            strategy.updated_at = datetime.utcnow()

            session.add(strategy)
            session.commit()
            session.refresh(strategy)

            logger.info("更新策略: %s", strategy_id)
            return self._to_response(strategy)

    async def delete_strategy(self, strategy_id: str) -> bool:
        """删除策略"""
        with get_session() as session:
            strategy = session.get(Strategy, strategy_id)
            if not strategy:
                return False
            session.delete(strategy)
            session.commit()
            logger.info("删除策略: %s", strategy_id)
            return True

    async def list_strategies(
        self,
        status: Optional[str] = None,
        limit: int = 20,
        offset: int = 0,
    ) -> tuple[list[StrategyResponse], int]:
        """列出策略"""
        base_stmt = select(Strategy)
        if status:
            base_stmt = base_stmt.where(Strategy.status == status)

        data_stmt = base_stmt.offset(offset).limit(limit)

        with get_session() as session:
            strategies = session.exec(data_stmt).all()
            total = session.exec(base_stmt).all()
            return [self._to_response(s) for s in strategies], len(total)

    async def validate_strategy(self, request: StrategyValidateRequest) -> StrategyValidateResponse:
        """验证策略代码"""
        errors = []
        warnings = []

        try:
            compile(request.code, "<string>", "exec")
        except SyntaxError as e:
            errors.append(f"语法错误: {e.msg} (行 {e.lineno})")
            return StrategyValidateResponse(valid=False, errors=errors, warnings=warnings, message="策略代码存在语法错误")

        if "class" not in request.code:
            warnings.append("建议定义策略类（继承 bt.Strategy）")
        if "bt.Strategy" not in request.code and "Strategy" not in request.code:
            warnings.append("建议继承 backtrader.Strategy 类")
        if "next" not in request.code.lower():
            warnings.append("策略应包含 next() 方法来处理每个bar")

        dangerous_keywords = ["__import__", "eval", "exec", "open", "file"]
        for keyword in dangerous_keywords:
            if keyword in request.code:
                warnings.append(f"检测到潜在危险操作: {keyword}")

        valid = len(errors) == 0
        return StrategyValidateResponse(
            valid=valid,
            errors=errors,
            warnings=warnings,
            message="策略代码验证通过" if valid else "策略代码验证失败",
        )

    async def list_builtin_strategies(self) -> list[dict]:
        """列出内置策略元数据"""
        return list_builtin_strategies()

    async def _assert_factors_exist(self, factor_ids: list[str]) -> None:
        """校验因子存在"""
        stmt = select(Factor.id).where(Factor.id.in_(factor_ids))
        with get_session() as session:
            existing = session.exec(stmt).all()

        missing = set(factor_ids) - set(existing)
        if missing:
            raise ValueError(f"因子不存在: {', '.join(sorted(missing))}")

    @staticmethod
    def _to_response(strategy: Strategy) -> StrategyResponse:
        return StrategyResponse(
            id=strategy.id,
            name=strategy.name,
            description=strategy.description,
            code=strategy.code,
            factor_ids=strategy.factor_ids or [],
            parameters=strategy.parameters or {},
            status=strategy.status,
            created_at=strategy.created_at.isoformat(),
            updated_at=strategy.updated_at.isoformat() if strategy.updated_at else None,
        )
