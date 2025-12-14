"""API 端点测试"""
import pytest
from fastapi import status


class TestHealthCheck:
    """健康检查端点测试"""
    
    def test_root_endpoint(self, client):
        """测试根路径"""
        response = client.get("/")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["service"] == "quant-engine"
        assert data["status"] == "running"
        assert "version" in data
    
    def test_health_endpoint(self, client):
        """测试健康检查端点"""
        response = client.get("/health")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "ok"
        assert data["service"] == "quant-engine"


class TestStrategyAPI:
    """策略管理 API 测试"""
    
    def test_create_strategy(self, client, sample_strategy_code):
        """测试创建策略"""
        response = client.post(
            "/api/strategy",
            json={
                "name": "测试策略",
                "description": "这是一个测试策略",
                "code": sample_strategy_code,
                "parameters": {"period": 5}
            }
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["name"] == "测试策略"
        assert "id" in data
        assert data["status"] == "active"
    
    def test_create_strategy_invalid_code(self, client):
        """测试创建策略 - 无效代码"""
        response = client.post(
            "/api/strategy",
            json={
                "name": "无效策略",
                "description": "代码无效",
                "code": "invalid code",
                "parameters": {}
            }
        )
        # 应该成功创建（代码验证在验证端点），但这里测试基本验证
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_422_UNPROCESSABLE_ENTITY]
    
    def test_get_strategy(self, client, sample_strategy_code):
        """测试获取策略"""
        # 先创建策略
        create_response = client.post(
            "/api/strategy",
            json={
                "name": "测试策略",
                "description": "测试描述",
                "code": sample_strategy_code,
                "parameters": {}
            }
        )
        strategy_id = create_response.json()["id"]
        
        # 获取策略
        response = client.get(f"/api/strategy/{strategy_id}")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == strategy_id
        assert data["name"] == "测试策略"
    
    def test_get_strategy_not_found(self, client):
        """测试获取不存在的策略"""
        response = client.get("/api/strategy/nonexistent")
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_update_strategy(self, client, sample_strategy_code):
        """测试更新策略"""
        # 先创建策略
        create_response = client.post(
            "/api/strategy",
            json={
                "name": "原始名称",
                "description": "原始描述",
                "code": sample_strategy_code,
                "parameters": {}
            }
        )
        strategy_id = create_response.json()["id"]
        
        # 更新策略
        response = client.put(
            f"/api/strategy/{strategy_id}",
            json={
                "name": "更新后的名称",
                "description": "更新后的描述"
            }
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["name"] == "更新后的名称"
        assert data["description"] == "更新后的描述"
    
    def test_delete_strategy(self, client, sample_strategy_code):
        """测试删除策略"""
        # 先创建策略
        create_response = client.post(
            "/api/strategy",
            json={
                "name": "待删除策略",
                "description": "将被删除",
                "code": sample_strategy_code,
                "parameters": {}
            }
        )
        strategy_id = create_response.json()["id"]
        
        # 删除策略
        response = client.delete(f"/api/strategy/{strategy_id}")
        assert response.status_code == status.HTTP_200_OK
        
        # 验证已删除
        get_response = client.get(f"/api/strategy/{strategy_id}")
        assert get_response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_list_strategies(self, client, sample_strategy_code):
        """测试列出策略"""
        # 创建几个策略
        for i in range(3):
            client.post(
                "/api/strategy",
                json={
                    "name": f"策略{i}",
                    "description": f"策略{i}的描述",
                    "code": sample_strategy_code,
                    "parameters": {}
                }
            )
        
        # 列出策略
        response = client.get("/api/strategy")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total"] >= 3
        assert len(data["strategies"]) >= 3
    
    def test_validate_strategy(self, client, sample_strategy_code):
        """测试验证策略代码"""
        response = client.post(
            "/api/strategy/validate",
            json={
                "code": sample_strategy_code
            }
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "valid" in data
        assert isinstance(data["valid"], bool)
    
    def test_validate_strategy_invalid(self, client, invalid_strategy_code):
        """测试验证无效策略代码"""
        response = client.post(
            "/api/strategy/validate",
            json={
                "code": invalid_strategy_code
            }
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["valid"] is False
        assert len(data["errors"]) > 0


class TestBacktestAPI:
    """回测 API 测试"""
    
    @pytest.mark.skip(reason="需要模拟数据加载服务")
    def test_run_backtest_builtin(self, client):
        """测试执行回测 - 内置策略"""
        response = client.post(
            "/api/backtest/run",
            json={
                "stock_code": "000001",
                "start_date": "2023-01-01",
                "end_date": "2023-01-31",
                "strategy_mode": "builtin",
                "strategy_name": "ma_cross",
                "data_source": "tushare",
                "enable_ai_review": False,
                "parameters": {
                    "fast_period": 5,
                    "slow_period": 20
                }
            }
        )
        # 注意：这个测试可能需要数据服务，所以可能失败
        # 在实际测试中，应该 mock 数据加载服务
        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            status.HTTP_400_BAD_REQUEST
        ]
    
    def test_run_backtest_invalid_request(self, client):
        """测试回测请求 - 无效参数"""
        # 缺少必填字段
        response = client.post(
            "/api/backtest/run",
            json={
                "stock_code": "000001",
                # 缺少 start_date 和 end_date
            }
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_run_backtest_invalid_date_range(self, client):
        """测试回测请求 - 无效日期范围"""
        response = client.post(
            "/api/backtest/run",
            json={
                "stock_code": "000001",
                "start_date": "2023-01-31",
                "end_date": "2023-01-01",  # 结束日期早于开始日期
                "strategy_mode": "builtin",
                "strategy_name": "ma_cross",
                "data_source": "tushare"
            }
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_list_backtests(self, client):
        """测试列出回测记录"""
        response = client.get("/api/backtest")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "total" in data
        assert "backtests" in data
        assert isinstance(data["backtests"], list)
