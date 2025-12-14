import uuid
from datetime import datetime, date, timedelta
from typing import Optional

from core.logger import get_logger
from schemas.factor import (
    FactorCreateRequest,
    FactorUpdateRequest,
    FactorResponse,
    FactorCalculateRequest,
    FactorCalculateResponse,
)

logger = get_logger(__name__)


class FactorService:
    """因子服务"""
    
    def __init__(self):
        """初始化因子服务"""
        self.factors: dict[str, dict] = {}  # 内存存储，生产环境应使用数据库
        self._init_default_factors()
    
    def _init_default_factors(self):
        """初始化默认因子"""
        default_factors = [
            {
                "name": "RSI",
                "description": "相对强弱指标（Relative Strength Index）",
                "category": "technical",
                "formula": "RSI = 100 - (100 / (1 + RS)), RS = 平均上涨幅度 / 平均下跌幅度",
                "parameters": {"period": 14}
            },
            {
                "name": "MACD",
                "description": "指数平滑移动平均线（Moving Average Convergence Divergence）",
                "category": "technical",
                "formula": "MACD = EMA(12) - EMA(26), Signal = EMA(MACD, 9)",
                "parameters": {"fast_period": 12, "slow_period": 26, "signal_period": 9}
            },
            {
                "name": "MA",
                "description": "移动平均线（Moving Average）",
                "category": "technical",
                "formula": "MA = (P1 + P2 + ... + Pn) / n",
                "parameters": {"period": 20}
            },
            {
                "name": "BOLL",
                "description": "布林带（Bollinger Bands）",
                "category": "technical",
                "formula": "中轨 = MA(n), 上轨 = 中轨 + k*σ, 下轨 = 中轨 - k*σ",
                "parameters": {"period": 20, "std_dev": 2}
            }
        ]
        
        for factor_data in default_factors:
            factor_id = f"factor_{uuid.uuid4().hex[:8]}"
            factor_data.update({
                "id": factor_id,
                "created_at": datetime.now().isoformat()
            })
            self.factors[factor_id] = factor_data
    
    async def create_factor(self, request: FactorCreateRequest) -> FactorResponse:
        """创建因子"""
        try:
            factor_id = f"factor_{uuid.uuid4().hex[:8]}"
            now = datetime.now().isoformat()
            
            factor_data = {
                "id": factor_id,
                "name": request.name,
                "description": request.description,
                "category": request.category,
                "formula": request.formula,
                "parameters": request.parameters,
                "created_at": now
            }
            
            self.factors[factor_id] = factor_data
            
            logger.info(f"创建因子: {factor_id} - {request.name}")
            
            return FactorResponse(**factor_data)
            
        except Exception as e:
            logger.error(f"创建因子失败: {e}", exc_info=True)
            raise
    
    async def get_factor(self, factor_id: str) -> Optional[FactorResponse]:
        """获取因子"""
        factor_data = self.factors.get(factor_id)
        if not factor_data:
            return None
        return FactorResponse(**factor_data)
    
    async def update_factor(
        self,
        factor_id: str,
        request: FactorUpdateRequest
    ) -> Optional[FactorResponse]:
        """更新因子"""
        factor_data = self.factors.get(factor_id)
        if not factor_data:
            return None
        
        # 更新字段
        update_data = request.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            if value is not None:
                factor_data[key] = value
        
        logger.info(f"更新因子: {factor_id}")
        
        return FactorResponse(**factor_data)
    
    async def delete_factor(self, factor_id: str) -> bool:
        """删除因子"""
        if factor_id in self.factors:
            del self.factors[factor_id]
            logger.info(f"删除因子: {factor_id}")
            return True
        return False
    
    async def list_factors(
        self,
        category: Optional[str] = None,
        limit: int = 20,
        offset: int = 0
    ) -> list[FactorResponse]:
        """列出因子"""
        factors = list(self.factors.values())
        
        # 按类别过滤
        if category:
            factors = [f for f in factors if f.get("category") == category]
        
        # 分页
        factors = factors[offset:offset + limit]
        
        return [FactorResponse(**f) for f in factors]
    
    async def calculate_factor(
        self,
        request: FactorCalculateRequest
    ) -> FactorCalculateResponse:
        """
        计算因子值
        
        注意：这是一个示例实现，实际需要：
        1. 从 TDengine 或数据库获取历史行情数据
        2. 根据因子公式计算因子值
        3. 返回时间序列数据
        """
        try:
            # 获取因子信息
            factor_data = self.factors.get(request.factor_id)
            if not factor_data:
                raise ValueError(f"因子不存在: {request.factor_id}")
            
            logger.info(
                f"计算因子: {factor_data['name']}, "
                f"标的: {request.symbol}, "
                f"{request.start_date} - {request.end_date}"
            )
            
            # 模拟因子计算（实际应从数据库获取数据并计算）
            values = await self._simulate_factor_calculation(request)
            
            return FactorCalculateResponse(
                factor_id=request.factor_id,
                symbol=request.symbol,
                start_date=request.start_date,
                end_date=request.end_date,
                values=values,
                total_points=len(values)
            )
            
        except Exception as e:
            logger.error(f"计算因子失败: {e}", exc_info=True)
            raise
    
    async def _simulate_factor_calculation(
        self,
        request: FactorCalculateRequest
    ) -> list[dict]:
        """模拟因子计算（示例实现）"""
        import random
        
        start = date.fromisoformat(request.start_date)
        end = date.fromisoformat(request.end_date)
        
        values = []
        current_date = start
        
        # 生成模拟因子值
        base_value = random.uniform(0, 100)
        while current_date <= end:
            # 模拟因子值波动
            change = random.uniform(-2.0, 2.0)
            base_value += change
            base_value = max(0, min(100, base_value))  # 限制在0-100范围
            
            values.append({
                "date": current_date.isoformat(),
                "value": round(base_value, 4)
            })
            
            current_date += timedelta(days=1)
        
        return values
