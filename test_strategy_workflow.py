"""
测试策略创建和回测流程
"""
import requests
import json
import time
from datetime import datetime, timedelta

BASE_URL = "http://localhost:8000"

# 测试用户凭证
TEST_USERNAME = "test_user"
TEST_PASSWORD = "test_password"
AUTH_TOKEN = None

# 简单的策略代码示例（基于 backtrader）
SIMPLE_STRATEGY_CODE = """
import backtrader as bt

class SimpleMovingAverageCrossover(bt.Strategy):
    params = (
        ('fast_period', 10),
        ('slow_period', 30),
    )
    
    def __init__(self):
        self.fast_ma = bt.indicators.SimpleMovingAverage(
            self.data.close, period=self.params.fast_period
        )
        self.slow_ma = bt.indicators.SimpleMovingAverage(
            self.data.close, period=self.params.slow_period
        )
        # 正确的写法：bt.indicators.CrossOver，不是 bt.CrossOver
        self.signal = bt.indicators.CrossOver(self.fast_ma, self.slow_ma)
    
    def next(self):
        if not self.position:
            if self.signal > 0:
                self.buy()
        elif self.signal < 0:
            self.close()
"""

def test_login():
    """测试登录"""
    global AUTH_TOKEN
    print("=" * 60)
    print("0. 测试登录")
    print("=" * 60)
    
    # 先尝试注册
    print("尝试注册用户...")
    register_payload = {
        "username": TEST_USERNAME,
        "password": TEST_PASSWORD
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/auth/register",
            json=register_payload,
            timeout=10
        )
        print(f"注册状态码: {response.status_code}")
        print(f"注册响应: {response.json()}")
    except Exception as e:
        print(f"注册错误（可能已存在）: {e}")
    
    # 尝试登录
    print("\n尝试登录...")
    login_payload = {
        "username": TEST_USERNAME,
        "password": TEST_PASSWORD
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/auth/login/json",
            json=login_payload,
            timeout=10
        )
        print(f"登录状态码: {response.status_code}")
        result = response.json()
        print(json.dumps(result, indent=2, ensure_ascii=False))
        
        if response.status_code == 200:
            token_data = result.get("data", {})
            AUTH_TOKEN = token_data.get("access_token")
            if AUTH_TOKEN:
                print(f"\n✅ 登录成功！Token: {AUTH_TOKEN[:50]}...")
                return True
            else:
                print(f"❌ 登录返回但未获取 token")
                return False
        else:
            print(f"❌ 登录失败")
            return False
    except Exception as e:
        print(f"❌ 登录错误: {e}")
        return False


def test_create_strategy():
    """测试创建策略"""
    print("=" * 60)
    print("1. 测试验证和创建策略")
    print("=" * 60)
    
    headers = {
        "Authorization": f"Bearer {AUTH_TOKEN}"
    }
    
    # 先验证策略代码
    print("\n验证策略代码...")
    validate_payload = {
        "code": SIMPLE_STRATEGY_CODE
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/strategy/validate",
            json=validate_payload,
            headers=headers,
            timeout=10
        )
        print(f"验证状态码: {response.status_code}")
        result = response.json()
        
        if response.status_code == 200:
            data = result.get("data", result)
            valid = data.get("valid", False)
            
            if valid:
                print(f"✅ 策略代码验证通过")
            else:
                print(f"❌ 策略代码验证失败:")
                for error in data.get("errors", []):
                    print(f"  - {error}")
                print("终止创建流程")
                return None
        else:
            print(f"⚠️ 验证请求失败，继续尝试创建")
    except Exception as e:
        print(f"⚠️ 验证错误: {e}，继续尝试创建")
    
    # 创建策略
    print("\n创建策略...")
    payload = {
        "name": "简单均线交叉策略",
        "description": "10周期快线与30周期慢线交叉策略",
        "code": SIMPLE_STRATEGY_CODE,
        "factor_ids": ["default"],
        "parameters": {
            "fast_period": 10,
            "slow_period": 30
        },
        "status": "draft"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/strategy",
            json=payload,
            headers=headers,
            timeout=10
        )
        print(f"状态码: {response.status_code}")
        print(f"响应内容:")
        result = response.json()
        print(json.dumps(result, indent=2, ensure_ascii=False))
        
        if response.status_code == 200:
            strategy_id = result.get("data", {}).get("id")
            print(f"\n✅ 策略创建成功！策略ID: {strategy_id}")
            return strategy_id
        else:
            print(f"\n❌ 创建策略失败")
            return None
    except Exception as e:
        print(f"❌ 错误: {e}")
        return None


def test_get_strategy(strategy_id):
    """测试获取策略"""
    print("\n" + "=" * 60)
    print("2. 测试获取策略")
    print("=" * 60)
    
    headers = {
        "Authorization": f"Bearer {AUTH_TOKEN}"
    }
    
    try:
        response = requests.get(
            f"{BASE_URL}/api/strategy/{strategy_id}",
            headers=headers,
            timeout=10
        )
        print(f"状态码: {response.status_code}")
        result = response.json()
        print(json.dumps(result, indent=2, ensure_ascii=False))
        
        if response.status_code == 200:
            print(f"✅ 策略获取成功")
        else:
            print(f"❌ 获取策略失败")
    except Exception as e:
        print(f"❌ 错误: {e}")


def test_backtest(strategy_id):
    """测试回测"""
    print("\n" + "=" * 60)
    print("3. 测试策略回测")
    print("=" * 60)
    
    # 设置回测日期范围（过去一年）
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=365)
    
    payload = {
        "stock_code": "000001",  # 平安银行
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),
        "strategy_mode": "custom",
        "strategy_code": SIMPLE_STRATEGY_CODE,  # 直接使用策略代码
        "data_source": "tushare",
        "initial_cash": 100000.0,
        "commission": 0.001,
        "slippage": 0.0,
        "parameters": {
            "fast_period": 10,
            "slow_period": 30
        }
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/backtest/run",
            json=payload,
            timeout=30
        )
        print(f"状态码: {response.status_code}")
        result = response.json()
        print(json.dumps(result, indent=2, ensure_ascii=False))
        
        if response.status_code == 200:
            backtest_id = result.get("data", {}).get("backtest_id")
            print(f"\n✅ 回测提交成功！回测ID: {backtest_id}")
            return backtest_id
        else:
            print(f"❌ 回测提交失败")
            return None
    except Exception as e:
        print(f"❌ 错误: {e}")
        return None


def test_get_backtest_result(backtest_id):
    """测试获取回测结果"""
    print("\n" + "=" * 60)
    print("4. 轮询获取回测结果")
    print("=" * 60)
    
    max_attempts = 10
    attempt = 0
    
    while attempt < max_attempts:
        try:
            response = requests.get(
                f"{BASE_URL}/api/backtest/{backtest_id}",
                timeout=10
            )
            print(f"第 {attempt + 1} 次尝试 - 状态码: {response.status_code}")
            result = response.json()
            
            data = result.get("data", {})
            status = data.get("status")
            print(f"回测状态: {status}")
            
            if status == "completed":
                print(f"\n✅ 回测完成！")
                print("回测结果摘要:")
                print(f"  总收益率: {data.get('metrics', {}).get('total_return', 'N/A')}")
                print(f"  夏普比率: {data.get('metrics', {}).get('sharpe_ratio', 'N/A')}")
                print(f"  最大回撤: {data.get('metrics', {}).get('max_drawdown', 'N/A')}")
                print(json.dumps(result, indent=2, ensure_ascii=False))
                return True
            elif status == "failed":
                print(f"❌ 回测失败: {data.get('error', 'Unknown error')}")
                return False
            else:
                print(f"⏳ 回测执行中，{5 + attempt * 2} 秒后重试...")
                time.sleep(5 + attempt * 2)
                attempt += 1
        except Exception as e:
            print(f"❌ 错误: {e}")
            return False
    
    print(f"❌ 回测超时（超过 {max_attempts * 5} 秒）")
    return False


def test_list_backtests():
    """测试列出回测记录"""
    print("\n" + "=" * 60)
    print("5. 测试列出回测记录")
    print("=" * 60)
    
    try:
        response = requests.get(
            f"{BASE_URL}/api/backtest",
            params={"limit": 5, "offset": 0},
            timeout=10
        )
        print(f"状态码: {response.status_code}")
        result = response.json()
        print(json.dumps(result, indent=2, ensure_ascii=False))
        
        if response.status_code == 200:
            print(f"✅ 列表获取成功")
        else:
            print(f"❌ 列表获取失败")
    except Exception as e:
        print(f"❌ 错误: {e}")


def test_login():


def main():
    """主测试流程"""
    global AUTH_TOKEN
    print("\n🚀 开始测试策略创建和回测流程\n")
    
    # 0. 登录
    if not test_login():
        print("\n❌ 登录失败，无法继续测试")
        return
    
    # 1. 创建策略
    strategy_id = test_create_strategy()
    if not strategy_id:
        print("\n❌ 策略创建失败，终止测试")
        return
    
    # 2. 获取策略
    test_get_strategy(strategy_id)
    
    # 3. 执行回测
    backtest_id = test_backtest(strategy_id)
    if not backtest_id:
        print("\n❌ 回测提交失败，终止测试")
        return
    
    # 4. 轮询获取回测结果
    test_get_backtest_result(backtest_id)
    
    # 5. 列出回测记录
    test_list_backtests()
    
    print("\n" + "=" * 60)
    print("✅ 测试完成")
    print("=" * 60)


if __name__ == "__main__":
    main()
