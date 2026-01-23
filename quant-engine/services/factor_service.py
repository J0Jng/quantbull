import re
from datetime import date, datetime, timedelta
from typing import Optional

from sqlmodel import or_, select

from core.logger import get_logger
from db import get_session
from models.factor import Factor, generate_factor_code
from schemas.factor import (
    ALLOWED_DATA_SOURCES,
    ALLOWED_EXPRESSION_COLUMNS,
    FactorCalculateRequest,
    FactorCalculateResponse,
    FactorCreateRequest,
    FactorResponse,
    FactorUpdateRequest,
    FactorValidateRequest,
    FactorValidateResponse,
)

logger = get_logger(__name__)


class FactorService:
    """因子服务，使用数据库持久化"""

    async def validate_expression(self, request: FactorValidateRequest) -> FactorValidateResponse:
        """验证因子表达式语法和有效性"""
        expression = request.expression.strip()
        errors = []
        warnings = []
        
        # 检查表达式是否为空
        if not expression:
            return FactorValidateResponse(
                valid=False,
                expression=expression,
                errors=["表达式不能为空"],
                warnings=[],
                suggested_fix=None,
                message="表达式验证失败",
            )
        
        # 提取表达式中使用的标识符
        # 匹配可能的列名：字母开头，包含字母、数字、下划线
        identifiers = set(re.findall(r'\b([a-zA-Z_][a-zA-Z0-9_]*)\b', expression))
        
        # 排除数学运算符和常见的数字表示
        math_keywords = {'and', 'or', 'not', 'in', 'is', 'True', 'False', 'None'}
        identifiers = identifiers - math_keywords
        
        # 检查是否有未知的列名
        unknown_columns = []
        used_columns = []
        for ident in identifiers:
            if ident in ALLOWED_EXPRESSION_COLUMNS:
                used_columns.append(ident)
            elif not ident.isdigit():
                unknown_columns.append(ident)
        
        if unknown_columns:
            errors.append(f"未知的列名: {', '.join(sorted(unknown_columns))}")
            # 提供建议的修正
            similar_cols = []
            for col in unknown_columns:
                for allowed in ALLOWED_EXPRESSION_COLUMNS:
                    if col.lower() in allowed.lower() or allowed.lower() in col.lower():
                        similar_cols.append(f"{col} → {allowed}")
                        break
            if similar_cols:
                warnings.append(f"可能的替代列名: {', '.join(similar_cols)}")
        
        # 检查危险的代码模式
        dangerous_patterns = [
            (r'\bimport\b', '不允许使用 import'),
            (r'\bexec\b', '不允许使用 exec'),
            (r'\beval\b', '不允许使用 eval'),
            (r'\b__\w+__\b', '不允许使用双下划线属性'),
            (r'\bopen\s*\(', '不允许使用 open 函数'),
            (r'\bos\s*\.', '不允许使用 os 模块'),
            (r'\bsys\s*\.', '不允许使用 sys 模块'),
        ]
        
        for pattern, msg in dangerous_patterns:
            if re.search(pattern, expression):
                errors.append(msg)
        
        # 检查括号是否匹配
        if expression.count('(') != expression.count(')'):
            errors.append("括号不匹配")
        
        # 尝试编译表达式检查语法
        suggested_fix = None
        if not errors:
            try:
                # 使用 pandas.eval 兼容的语法检查
                compile(expression, '<expression>', 'eval')
            except SyntaxError as e:
                errors.append(f"语法错误: {e.msg}")
                # 尝试给出修正建议
                if '=' in expression and '==' not in expression:
                    suggested_fix = expression.replace('=', '==')
                    warnings.append("提示: 比较运算符应该使用 '==' 而不是 '='")
        
        # 检查表达式复杂度
        if len(expression) > 500:
            warnings.append("表达式过长，建议拆分为多个因子")
        
        # 生成使用说明
        if used_columns and not errors:
            warnings.append(f"表达式使用了以下列: {', '.join(sorted(used_columns)[:5])}{'...' if len(used_columns) > 5 else ''}")
        
        return FactorValidateResponse(
            valid=len(errors) == 0,
            expression=expression,
            errors=errors,
            warnings=warnings,
            suggested_fix=suggested_fix,
            message="表达式验证通过" if len(errors) == 0 else "表达式验证失败",
        )

    async def create_factor(self, request: FactorCreateRequest) -> FactorResponse:
        """创建因子"""
        if request.data_source not in ALLOWED_DATA_SOURCES:
            raise ValueError(f"data_source 必须是: {', '.join(ALLOWED_DATA_SOURCES)}")

        # 生成唯一的因子代码
        factor_code = getattr(request, 'code', None) or generate_factor_code()
        
        factor = Factor(
            name=request.name,
            code=factor_code,
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
            
            # 更新 updated_at 时间戳
            factor.updated_at = datetime.now()

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
        search: Optional[str] = None,
        limit: int = 20,
        offset: int = 0,
    ) -> tuple[list[FactorResponse], int]:
        """列出因子，支持类别筛选和搜索"""
        base_stmt = select(Factor)
        
        # 类别筛选
        if category:
            base_stmt = base_stmt.where(Factor.category == category)
        
        # 搜索：支持名称、代码、描述模糊搜索
        if search:
            search_pattern = f"%{search}%"
            base_stmt = base_stmt.where(
                or_(
                    Factor.name.ilike(search_pattern),
                    Factor.code.ilike(search_pattern),
                    Factor.description.ilike(search_pattern),
                )
            )

        # 按创建时间倒序排列
        data_stmt = base_stmt.order_by(Factor.created_at.desc()).offset(offset).limit(limit)

        with get_session() as session:
            factors = session.exec(data_stmt).all()
            # 计算总数
            from sqlmodel import func
            count_stmt = select(func.count()).select_from(base_stmt.subquery())
            total = session.exec(count_stmt).one()
            return [self._to_response(f) for f in factors], total

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
            code=factor.code or "",
            name=factor.name,
            description=factor.description,
            expression=factor.expression,
            data_source=factor.data_source,
            category=factor.category,
            formula=factor.formula,
            parameters=factor.parameters or {},
            created_at=factor.created_at.isoformat() if factor.created_at else "",
            updated_at=factor.updated_at.isoformat() if factor.updated_at else None,
        )
