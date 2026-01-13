import ast
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
from services.strategy_examples import get_strategy_examples

logger = get_logger(__name__)


class StrategyService:
    """策略服务，使用数据库持久化"""

    async def create_strategy(self, request: StrategyCreateRequest) -> StrategyResponse:
        """创建策略"""
        if not request.factor_ids:
            raise ValueError("factor_ids 不允许为空")
        if request.status not in ALLOWED_STATUSES:
            raise ValueError(f"status 必须是: {', '.join(ALLOWED_STATUSES)}")

        # 验证因子存在性（允许 "default" 作为占位符）
        if request.factor_ids != ["default"]:
            try:
                await self._assert_factors_exist(request.factor_ids)
            except Exception as e:
                logger.warning(f"因子验证失败，但继续创建策略: {e}")

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
                # 验证因子存在性（允许 "default" 作为占位符）
                if factor_ids != ["default"]:
                    try:
                        self._assert_factors_exist(factor_ids)
                    except Exception as e:
                        logger.warning(f"因子验证失败，但继续更新策略: {e}")

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
        search: Optional[str] = None,
        limit: int = 20,
        offset: int = 0,
    ) -> tuple[list[StrategyResponse], int]:
        """列出策略"""
        base_stmt = select(Strategy)
        
        # 状态筛选
        if status:
            base_stmt = base_stmt.where(Strategy.status == status)
        
        # 搜索功能：对 name 和 description 进行模糊匹配
        if search:
            search_pattern = f"%{search}%"
            base_stmt = base_stmt.where(
                (Strategy.name.ilike(search_pattern)) | 
                (Strategy.description.ilike(search_pattern))
            )

        # 分页查询
        data_stmt = base_stmt.offset(offset).limit(limit)

        with get_session() as session:
            strategies = session.exec(data_stmt).all()
            # 获取总数
            count_result = session.exec(base_stmt).all()
            total = len(count_result)
            return [self._to_response(s) for s in strategies], total

    async def validate_strategy(self, request: StrategyValidateRequest) -> StrategyValidateResponse:
        """验证策略代码（AST 静态分析）"""
        errors = []
        warnings = []

        # 1. 语法检查
        try:
            tree = ast.parse(request.code)
        except SyntaxError as e:
            line_info = f"第{e.lineno}行" if e.lineno else ""
            col_info = f"第{e.offset}列" if e.offset else ""
            location = f"{line_info}{col_info}: " if line_info or col_info else ""
            errors.append(f"{location}语法错误: {e.msg}")
            return StrategyValidateResponse(
                valid=False, 
                errors=errors, 
                warnings=warnings, 
                message="策略代码存在语法错误"
            )
        except Exception as e:
            errors.append(f"代码解析失败: {str(e)}")
            return StrategyValidateResponse(
                valid=False,
                errors=errors,
                warnings=warnings,
                message="策略代码解析失败"
            )

        # 2. 安全检查：禁止危险的导入和调用
        dangerous_imports = {
            'os', 'sys', 'subprocess', 'socket', 'shutil', 
            'pathlib', 'importlib', 'builtins', 'requests',
            '__builtin__', 'pickle', 'shelve', 'tempfile'
        }
    
    async def get_strategy_examples(self) -> list[dict]:
        """获取策略示例代码"""
        return get_strategy_examples()
        dangerous_calls = {
            'eval', 'exec', 'compile', 'open', '__import__', 
            'input', 'execfile', 'reload'
        }

        for node in ast.walk(tree):
            # 检查导入语句
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name in dangerous_imports:
                        line = getattr(node, 'lineno', '?')
                        errors.append(f"第{line}行: 禁止导入危险模块 '{alias.name}'")
            
            elif isinstance(node, ast.ImportFrom):
                if node.module and node.module.split('.')[0] in dangerous_imports:
                    line = getattr(node, 'lineno', '?')
                    errors.append(f"第{line}行: 禁止导入危险模块 '{node.module}'")
            
            # 检查函数调用
            elif isinstance(node, ast.Call):
                func_name = None
                if isinstance(node.func, ast.Name):
                    func_name = node.func.id
                elif isinstance(node.func, ast.Attribute):
                    func_name = node.func.attr
                
                if func_name in dangerous_calls:
                    line = getattr(node, 'lineno', '?')
                    errors.append(f"第{line}行: 禁止调用危险函数 '{func_name}'")

        # 如果有安全错误，立即返回
        if errors:
            return StrategyValidateResponse(
                valid=False,
                errors=errors,
                warnings=warnings,
                message="策略代码存在安全风险"
            )

        # 3. 结构检查：必须有 Strategy 类
        strategy_classes = []
        has_next_method = False

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                # 检查是否继承 Strategy 或 bt.Strategy
                for base in node.bases:
                    base_name = ""
                    if isinstance(base, ast.Name):
                        base_name = base.id
                    elif isinstance(base, ast.Attribute):
                        # 处理 bt.Strategy 这种形式
                        base_name = base.attr
                    
                    if "Strategy" in base_name:
                        strategy_classes.append(node.name)
                        
                        # 检查类中是否有 next 方法
                        for item in node.body:
                            if isinstance(item, ast.FunctionDef) and item.name == "next":
                                has_next_method = True
                                break

        if not strategy_classes:
            errors.append("缺少策略类定义: 必须定义一个继承自 bt.Strategy 或 Strategy 的类")
        
        if strategy_classes and not has_next_method:
            errors.append(f"策略类 {strategy_classes[0]} 缺少 next() 方法: 回测引擎需要 next() 方法来处理每个数据点")

        # 4. 建议性检查（warnings）
        has_init = False
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and node.name in strategy_classes:
                for item in node.body:
                    if isinstance(item, ast.FunctionDef) and item.name == "__init__":
                        has_init = True
                        break

        if strategy_classes and not has_init:
            warnings.append(f"建议在策略类中定义 __init__ 方法来初始化指标")

        # 返回验证结果
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

    def _assert_factors_exist(self, factor_ids: list[str]) -> None:
        """校验因子存在"""
        try:
            stmt = select(Factor.id).where(Factor.id.in_(factor_ids))
            with get_session() as session:
                existing = session.exec(stmt).all()

            missing = set(factor_ids) - set(existing)
            if missing:
                raise ValueError(f"因子不存在: {', '.join(sorted(missing))}")
        except Exception as e:
            logger.error(f"检查因子存在性时出错: {e}", exc_info=True)
            raise

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
