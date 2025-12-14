"""服务层测试"""
import pytest
from unittest.mock import patch, MagicMock
import pandas as pd

from services.backtest_service import BacktestService
from services.strategy_service import StrategyService
from schemas.backtest import BacktestRequest
from schemas.strategy import StrategyCreateRequest, StrategyUpdateRequest, StrategyValidateRequest
from tests.test_utils import create_mock_market_data


class TestStrategyService:
    """策略服务测试"""
    
    @pytest.fixture
    def service(self):
        """创建策略服务实例"""
        return StrategyService()
    
    @pytest.fixture
    def sample_strategy_code(self):
        """示例策略代码"""
        return """
import backtrader as bt

class TestStrategy(bt.Strategy):
    def __init__(self):
        self.sma = bt.indicators.SMA(self.data.close, period=5)
        self.order = None
    
    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            return
        self.order = None
    
    def next(self):
        if self.order:
            return
        if not self.position:
            if self.data.close[0] > self.sma[0]:
                self.order = self.buy()
        else:
            if self.data.close[0] < self.sma[0]:
                self.order = self.sell()
"""
    
    @pytest.mark.asyncio
    async def test_create_strategy(self, service, sample_strategy_code):
        """测试创建策略"""
        request = StrategyCreateRequest(
            name="测试策略",
            description="测试描述",
            code=sample_strategy_code,
            parameters={"period": 5}
        )
        
        result = await service.create_strategy(request)
        
        assert result.name == "测试策略"
        assert result.description == "测试描述"
        # 代码可能被去除首尾空白，所以只检查包含关键内容
        assert "class TestStrategy" in result.code
        assert "bt.Strategy" in result.code
        assert result.id is not None
        assert result.id.startswith("strategy_")
        assert result.status == "active"
    
    @pytest.mark.asyncio
    async def test_get_strategy(self, service, sample_strategy_code):
        """测试获取策略"""
        # 先创建
        create_request = StrategyCreateRequest(
            name="测试策略",
            description="测试",
            code=sample_strategy_code,
            parameters={}
        )
        created = await service.create_strategy(create_request)
        
        # 获取
        result = await service.get_strategy(created.id)
        
        assert result is not None
        assert result.id == created.id
        assert result.name == "测试策略"
    
    @pytest.mark.asyncio
    async def test_get_strategy_not_found(self, service):
        """测试获取不存在的策略"""
        result = await service.get_strategy("nonexistent")
        assert result is None
    
    @pytest.mark.asyncio
    async def test_update_strategy(self, service, sample_strategy_code):
        """测试更新策略"""
        # 先创建
        create_request = StrategyCreateRequest(
            name="原始名称",
            description="原始描述",
            code=sample_strategy_code,
            parameters={}
        )
        created = await service.create_strategy(create_request)
        
        # 更新
        update_request = StrategyUpdateRequest(
            name="更新后的名称",
            description="更新后的描述"
        )
        result = await service.update_strategy(created.id, update_request)
        
        assert result is not None
        assert result.name == "更新后的名称"
        assert result.description == "更新后的描述"
    
    @pytest.mark.asyncio
    async def test_delete_strategy(self, service, sample_strategy_code):
        """测试删除策略"""
        # 先创建
        create_request = StrategyCreateRequest(
            name="待删除策略",
            description="测试",
            code=sample_strategy_code,
            parameters={}
        )
        created = await service.create_strategy(create_request)
        
        # 删除
        result = await service.delete_strategy(created.id)
        assert result is True
        
        # 验证已删除
        get_result = await service.get_strategy(created.id)
        assert get_result is None
    
    @pytest.mark.asyncio
    async def test_list_strategies(self, service, sample_strategy_code):
        """测试列出策略"""
        # 创建多个策略
        for i in range(5):
            request = StrategyCreateRequest(
                name=f"策略{i}",
                description=f"描述{i}",
                code=sample_strategy_code,
                parameters={}
            )
            await service.create_strategy(request)
        
        # 列出
        result = await service.list_strategies()
        assert len(result) >= 5
    
    @pytest.mark.asyncio
    async def test_validate_strategy_valid(self, service, sample_strategy_code):
        """测试验证有效策略"""
        request = StrategyValidateRequest(code=sample_strategy_code)
        result = await service.validate_strategy(request)
        
        assert result.valid is True
        assert len(result.errors) == 0
    
    @pytest.mark.asyncio
    async def test_validate_strategy_invalid(self, service):
        """测试验证无效策略"""
        invalid_code = """
import backtrader as bt

class TestStrategy(bt.Strategy):
    def next(self):
        print(hello world)  # 语法错误
"""
        request = StrategyValidateRequest(code=invalid_code)
        result = await service.validate_strategy(request)
        
        assert result.valid is False
        assert len(result.errors) > 0


class TestBacktestService:
    """回测服务测试"""
    
    @pytest.fixture
    def service(self):
        """创建回测服务实例"""
        return BacktestService()
    
    @pytest.mark.asyncio
    @patch("services.backtest_service.load_market_data")
    async def test_run_backtest_builtin(self, mock_load_data, service):
        """测试执行回测 - 内置策略（使用模拟数据）"""
        # 创建模拟数据
        mock_df = create_mock_market_data(
            stock_code="000001",
            start_date="2023-01-01",
            end_date="2023-01-31",
            base_price=10.0
        )
        mock_load_data.return_value = mock_df
        
        # 创建回测请求
        request = BacktestRequest(
            stock_code="000001",
            start_date="2023-01-01",
            end_date="2023-01-31",
            strategy_mode="builtin",
            strategy_name="ma_cross",
            data_source="tushare",
            enable_ai_review=False,
            parameters={
                "fast_period": 5,
                "slow_period": 20
            }
        )
        
        # 执行回测
        result = await service.run_backtest(request)
        
        # 验证结果
        assert result.success is True
        assert result.backtest_id is not None
        assert result.backtest_id.startswith("backtest_")
        assert result.metrics is not None
        assert len(result.daily_nav) > 0
        
        # 验证指标
        metrics = result.metrics
        assert "total_return" in metrics or "final_value" in metrics
    
    @pytest.mark.asyncio
    @patch("services.backtest_service.load_market_data")
    async def test_run_backtest_custom(self, mock_load_data, service):
        """测试执行回测 - 自定义策略"""
        # 创建模拟数据
        mock_df = create_mock_market_data(
            stock_code="000001",
            start_date="2023-01-01",
            end_date="2023-01-31"
        )
        mock_load_data.return_value = mock_df
        
        # 自定义策略代码
        strategy_code = """
import backtrader as bt

class CustomStrategy(bt.Strategy):
    def __init__(self):
        self.sma = bt.indicators.SMA(self.data.close, period=5)
        self.order = None
    
    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            return
        self.order = None
    
    def next(self):
        if self.order:
            return
        if not self.position:
            if self.data.close[0] > self.sma[0]:
                self.order = self.buy()
        else:
            if self.data.close[0] < self.sma[0]:
                self.order = self.sell()
"""
        
        request = BacktestRequest(
            stock_code="000001",
            start_date="2023-01-01",
            end_date="2023-01-31",
            strategy_mode="custom",
            strategy_code=strategy_code,
            data_source="tushare",
            enable_ai_review=False
        )
        
        result = await service.run_backtest(request)
        
        assert result.success is True
        assert len(result.daily_nav) > 0
    
    @pytest.mark.asyncio
    @patch("services.backtest_service.load_market_data")
    async def test_run_backtest_with_ai_review(self, mock_load_data, service):
        """测试执行回测 - 启用 AI 评价"""
        # 创建模拟数据
        mock_df = create_mock_market_data(
            stock_code="000001",
            start_date="2023-01-01",
            end_date="2023-01-31"
        )
        mock_load_data.return_value = mock_df
        
        request = BacktestRequest(
            stock_code="000001",
            start_date="2023-01-01",
            end_date="2023-01-31",
            strategy_mode="builtin",
            strategy_name="ma_cross",
            data_source="tushare",
            enable_ai_review=True,
            parameters={"fast_period": 5, "slow_period": 20}
        )
        
        result = await service.run_backtest(request)
        
        assert result.success is True
        # AI 评价数据可能为 None（如果提取失败）
        # 但基础指标应该存在
        assert result.metrics is not None
    
    @pytest.mark.asyncio
    @patch("services.backtest_service.load_market_data")
    async def test_run_backtest_empty_data(self, mock_load_data, service):
        """测试回测 - 空数据"""
        # 模拟空数据
        mock_load_data.return_value = pd.DataFrame()
        
        request = BacktestRequest(
            stock_code="000001",
            start_date="2023-01-01",
            end_date="2023-01-31",
            strategy_mode="builtin",
            strategy_name="ma_cross",
            data_source="tushare"
        )
        
        with pytest.raises(ValueError, match="未获取到行情数据"):
            await service.run_backtest(request)
    
    @pytest.mark.asyncio
    async def test_get_backtest(self, service):
        """测试获取回测结果"""
        # 先执行一个回测（需要 mock）
        # 这里只测试获取功能
        result = await service.get_backtest("nonexistent")
        assert result is None
    
    @pytest.mark.asyncio
    async def test_list_backtests(self, service):
        """测试列出回测记录"""
        result = await service.list_backtests(limit=10, offset=0)
        assert isinstance(result, list)
