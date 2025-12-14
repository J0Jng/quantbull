import uuid
from datetime import datetime
from typing import Optional

from core.logger import get_logger
from schemas.strategy import (
    StrategyCreateRequest,
    StrategyUpdateRequest,
    StrategyResponse,
    StrategyValidateRequest,
    StrategyValidateResponse,
)

logger = get_logger(__name__)


class StrategyService:
    """策略服务"""
    
    def __init__(self):
        """初始化策略服务"""
        self.strategies: dict[str, dict] = {}  # 内存存储，生产环境应使用数据库
    
    async def create_strategy(self, request: StrategyCreateRequest) -> StrategyResponse:
        """创建策略"""
        try:
            strategy_id = f"strategy_{uuid.uuid4().hex[:8]}"
            now = datetime.now().isoformat()
            
            strategy_data = {
                "id": strategy_id,
                "name": request.name,
                "description": request.description,
                "code": request.code,
                "parameters": request.parameters,
                "status": "active",
                "created_at": now,
                "updated_at": now
            }
            
            self.strategies[strategy_id] = strategy_data
            
            logger.info(f"创建策略: {strategy_id} - {request.name}")
            
            return StrategyResponse(**strategy_data)
            
        except Exception as e:
            logger.error(f"创建策略失败: {e}", exc_info=True)
            raise
    
    async def get_strategy(self, strategy_id: str) -> Optional[StrategyResponse]:
        """获取策略"""
        strategy_data = self.strategies.get(strategy_id)
        if not strategy_data:
            return None
        return StrategyResponse(**strategy_data)
    
    async def update_strategy(
        self, 
        strategy_id: str, 
        request: StrategyUpdateRequest
    ) -> Optional[StrategyResponse]:
        """更新策略"""
        strategy_data = self.strategies.get(strategy_id)
        if not strategy_data:
            return None
        
        # 更新字段
        update_data = request.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            if value is not None:
                strategy_data[key] = value
        
        strategy_data["updated_at"] = datetime.now().isoformat()
        
        logger.info(f"更新策略: {strategy_id}")
        
        return StrategyResponse(**strategy_data)
    
    async def delete_strategy(self, strategy_id: str) -> bool:
        """删除策略"""
        if strategy_id in self.strategies:
            del self.strategies[strategy_id]
            logger.info(f"删除策略: {strategy_id}")
            return True
        return False
    
    async def list_strategies(
        self, 
        status: Optional[str] = None,
        limit: int = 20,
        offset: int = 0
    ) -> list[StrategyResponse]:
        """列出策略"""
        strategies = list(self.strategies.values())
        
        # 按状态过滤
        if status:
            strategies = [s for s in strategies if s.get("status") == status]
        
        # 分页
        strategies = strategies[offset:offset + limit]
        
        return [StrategyResponse(**s) for s in strategies]
    
    async def validate_strategy(
        self, 
        request: StrategyValidateRequest
    ) -> StrategyValidateResponse:
        """
        验证策略代码
        
        检查：
        1. Python 语法
        2. 必要的类和方法
        3. Backtrader 兼容性
        """
        errors = []
        warnings = []
        
        try:
            # 检查语法
            compile(request.code, "<string>", "exec")
        except SyntaxError as e:
            errors.append(f"语法错误: {e.msg} (行 {e.lineno})")
            return StrategyValidateResponse(
                valid=False,
                errors=errors,
                warnings=warnings,
                message="策略代码存在语法错误"
            )
        
        # 检查是否包含必要的类（示例检查）
        if "class" not in request.code:
            warnings.append("建议定义策略类（继承 bt.Strategy）")
        
        if "bt.Strategy" not in request.code and "Strategy" not in request.code:
            warnings.append("建议继承 backtrader.Strategy 类")
        
        if "next" not in request.code.lower():
            warnings.append("策略应包含 next() 方法来处理每个bar")
        
        # 检查危险操作
        dangerous_keywords = ["__import__", "eval", "exec", "open", "file"]
        for keyword in dangerous_keywords:
            if keyword in request.code:
                warnings.append(f"检测到潜在危险操作: {keyword}")
        
        valid = len(errors) == 0
        
        return StrategyValidateResponse(
            valid=valid,
            errors=errors,
            warnings=warnings,
            message="策略代码验证通过" if valid else "策略代码验证失败"
        )
