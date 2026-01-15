#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试策略创建和回测流程
1. 登录获取 token
2. 创建策略
3. 获取策略信息
4. 提交回测任务
5. 轮询回测结果
6. 列出回测记录
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
    except Exception as e:
        print(f"注册错误（可能已存在）: {e}")
    
    # 尝试登录
    print("尝试登录...")
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
        
        if response.status_code == 200:
            token_data = result.get("data", {})
            AUTH_TOKEN = token_data.get("access_token")
            if AUTH_TOKEN:
                print(f"✅ 登录成功！")
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


def test_create_factors():
    """创建测试因子"""
    print("\n" + "=" * 60)
    print("1. 创建因子（ma_10, ma_30）")
    print("=" * 60)
    
    headers = {
        "Authorization": f"Bearer {AUTH_TOKEN}"
    }
    
    factors = [
        {
            "name": "10日均线偏离度",
            "description": "收盘价相对10日均线的偏离程度",
            "expression": "(close - MA_10) / MA_10",
            "data_source": "tushare",
            "category": "technical",
            "parameters": {"period": 10}
        },
        {
            "name": "30日均线偏离度",
            "description": "收盘价相对30日均线的偏离程度",
            "expression": "(close - MA_60) / MA_60",
            "data_source": "tushare",
            "category": "technical",
            "parameters": {"period": 30}
        },
        {
            "name": "RSI超卖指标",
            "description": "14日RSI指标",
            "expression": "RSI_14",
            "data_source": "tushare",
            "category": "technical",
            "parameters": {}
        }
    ]
    
    factor_ids = []
    for factor_def in factors:
        try:
            response = requests.post(
                f"{BASE_URL}/api/factor",
                json=factor_def,
                headers=headers,
                timeout=10
            )
            print(f"创建 {factor_def['name']} - 状态码: {response.status_code}")
            result = response.json()
            
            if response.status_code == 200:
                factor_id = result.get("data", {}).get("id")
                if factor_id:
                    factor_ids.append(factor_id)
                    print(f"  ✅ 创建成功！因子ID: {factor_id}")
            else:
                print(f"  ⚠️ 创建失败或已存在: {result.get('message', 'Unknown error')}")
        except Exception as e:
            print(f"  ⚠️ 错误: {e}")
    
    # 如果没有成功创建因子，使用默认值
    if not factor_ids:
        print("  使用默认因子ID")
        factor_ids = ["default"]
    
    return factor_ids


def test_validate_strategy():
    """测试策略代码验证"""
    print("\n" + "=" * 60)
    print("1.5. 测试策略代码验证")
    print("=" * 60)
    
    headers = {
        "Authorization": f"Bearer {AUTH_TOKEN}"
    }
    
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
        print(f"状态码: {response.status_code}")
        result = response.json()
        print(f"响应内容: {json.dumps(result, indent=2, ensure_ascii=False)}")
        
        if response.status_code == 200:
            data = result.get("data", result)
            valid = data.get("valid", False)
            
            if valid:
                print(f"✅ 策略代码验证通过！")
                if data.get("warnings"):
                    print(f"⚠️ 警告: {', '.join(data.get('warnings'))}")
                return True
            else:
                print(f"❌ 策略代码验证失败:")
                for error in data.get("errors", []):
                    print(f"  - {error}")
                return False
        else:
            print(f"❌ 验证请求失败")
            return False
    except Exception as e:
        print(f"❌ 验证错误: {e}")
        return False


def test_validate_factor_expression():
    """测试因子表达式验证"""
    print("\n" + "=" * 60)
    print("1.6. 测试因子表达式验证")
    print("=" * 60)
    
    headers = {
        "Authorization": f"Bearer {AUTH_TOKEN}"
    }
    
    # 测试用例：有效表达式
    valid_expressions = [
        "(close - MA_20) / MA_20",
        "RSI_14",
        "MACD - MACD_signal",
        "(close - BOLL_lower) / (BOLL_upper - BOLL_lower)"
    ]
    
    # 测试用例：无效表达式
    invalid_expressions = [
        "import os; os.system('rm -rf /')",  # 危险代码
        "unknown_column + close",  # 未知列名
        "(close - MA_20",  # 括号不匹配
    ]
    
    print("\n测试有效表达式:")
    for expr in valid_expressions:
        try:
            response = requests.post(
                f"{BASE_URL}/api/factor/validate",
                json={"expression": expr},
                headers=headers,
                timeout=10
            )
            result = response.json()
            data = result.get("data", result)
            valid = data.get("valid", False)
            print(f"  表达式: {expr[:40]}... => {'✅ 有效' if valid else '❌ 无效'}")
        except Exception as e:
            print(f"  ❌ 错误: {e}")
    
    print("\n测试无效表达式:")
    for expr in invalid_expressions:
        try:
            response = requests.post(
                f"{BASE_URL}/api/factor/validate",
                json={"expression": expr},
                headers=headers,
                timeout=10
            )
            result = response.json()
            data = result.get("data", result)
            valid = data.get("valid", False)
            errors = data.get("errors", [])
            print(f"  表达式: {expr[:40]}... => {'❌ 应该无效但通过' if valid else '✅ 正确识别无效'}")
            if errors:
                print(f"    错误: {errors[0]}")
        except Exception as e:
            print(f"  ❌ 错误: {e}")
    
    return True


def test_create_strategy(factor_ids):
    """测试创建策略"""
    print("\n" + "=" * 60)
    print("2. 测试创建策略")
    print("=" * 60)
    
    payload = {
        "name": "简单均线交叉策略",
        "description": "10周期快线与30周期慢线交叉策略",
        "code": SIMPLE_STRATEGY_CODE,
        "factor_ids": factor_ids,
        "parameters": {
            "fast_period": 10,
            "slow_period": 30
        },
        "status": "active"
    }
    
    headers = {
        "Authorization": f"Bearer {AUTH_TOKEN}"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/strategy",
            json=payload,
            headers=headers,
            timeout=10
        )
        print(f"状态码: {response.status_code}")
        result = response.json()
        print(f"响应内容: {json.dumps(result, indent=2, ensure_ascii=False)}")
        
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
    print("3. 测试获取策略")
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
        print(f"响应内容: {json.dumps(result, indent=2, ensure_ascii=False)}")
        
        if response.status_code == 200:
            print(f"✅ 策略获取成功")
        else:
            print(f"❌ 获取策略失败")
    except Exception as e:
        print(f"❌ 错误: {e}")


def test_backtest():
    """测试回测"""
    print("\n" + "=" * 60)
    print("4. 测试策略回测")
    print("=" * 60)
    
    # 设置回测日期范围（过去一年）
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=365)
    
    payload = {
        "stock_code": "000001",
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),
        "strategy_mode": "custom",
        "strategy_code": SIMPLE_STRATEGY_CODE,
        "data_source": "tushare",
        "initial_cash": 100000.0,
        "commission": 0.001,
        "slippage": 0.0,
        "parameters": {
            "fast_period": 10,
            "slow_period": 30
        }
    }
    
    headers = {
        "Authorization": f"Bearer {AUTH_TOKEN}"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/backtest/run",
            json=payload,
            headers=headers,
            timeout=30
        )
        print(f"状态码: {response.status_code}")
        result = response.json()
        print(f"响应内容: {json.dumps(result, indent=2, ensure_ascii=False)}")
        
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
    print("5. 轮询获取回测结果")
    print("=" * 60)
    
    headers = {
        "Authorization": f"Bearer {AUTH_TOKEN}"
    }
    
    max_attempts = 30
    attempt = 0
    
    while attempt < max_attempts:
        try:
            response = requests.get(
                f"{BASE_URL}/api/backtest/{backtest_id}",
                headers=headers,
                timeout=10
            )
            print(f"第 {attempt + 1} 次尝试 - 状态码: {response.status_code}")
            result = response.json()
            
            data = result.get("data", {})
            status = data.get("status")
            print(f"回测状态: {status}")
            
            # 回测完成状态可能是 'completed' 或 'success'
            if status in ("completed", "success"):
                print(f"\n✅ 回测完成！")
                print("回测结果摘要:")
                metrics = data.get('metrics', {})
                print(f"  总收益率: {metrics.get('total_return', 'N/A')}")
                print(f"  夏普比率: {metrics.get('sharpe_ratio', 'N/A')}")
                print(f"  最大回撤: {metrics.get('max_drawdown', 'N/A')}")
                print("\n完整结果:")
                print(json.dumps(result, indent=2, ensure_ascii=False))
                return True
            elif status == "failed":
                print(f"❌ 回测失败: {data.get('error', 'Unknown error')}")
                print(f"❌ 错误消息: {data.get('message', 'No message')}")
                return False
            else:
                wait_time = min(5 + attempt, 30)
                print(f"⏳ 回测执行中，{wait_time} 秒后重试...")
                time.sleep(wait_time)
                attempt += 1
        except Exception as e:
            print(f"❌ 错误: {e}")
            return False
    
    print(f"❌ 回测超时")
    return False


def test_list_backtests():
    """测试列出回测记录"""
    print("\n" + "=" * 60)
    print("6. 测试列出回测记录")
    print("=" * 60)
    
    headers = {
        "Authorization": f"Bearer {AUTH_TOKEN}"
    }
    
    try:
        response = requests.get(
            f"{BASE_URL}/api/backtest",
            params={"limit": 5, "offset": 0},
            headers=headers,
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


def main():
    """主测试流程"""
    global AUTH_TOKEN
    print("\n🚀 开始测试策略创建和回测流程\n")
    
    # 0. 登录
    if not test_login():
        print("\n❌ 登录失败，无法继续测试")
        return
    
    # 1. 创建因子
    factor_ids = test_create_factors()
    
    # 1.5. 验证策略代码
    if not test_validate_strategy():
        print("\n⚠️ 策略代码验证未通过，但继续测试流程")
    
    # 1.6. 验证因子表达式
    test_validate_factor_expression()
    
    # 2. 创建策略
    strategy_id = test_create_strategy(factor_ids)
    if not strategy_id:
        print("\n❌ 策略创建失败，终止测试")
        return
    
    # 3. 获取策略
    test_get_strategy(strategy_id)
    
    # 4. 执行回测
    backtest_id = test_backtest()
    if not backtest_id:
        print("\n❌ 回测提交失败，终止测试")
        return
    
    # 5. 轮询获取回测结果
    test_get_backtest_result(backtest_id)
    
    # 6. 列出回测记录
    test_list_backtests()
    
    print("\n" + "=" * 60)
    print("✅ 测试完成")
    print("=" * 60)


if __name__ == "__main__":
    main()
