"""测试脚本：验证行业排名功能（数据库版本）"""
import requests
import time

BASE_URL = "http://localhost:8000"

def test_industry_rank_api():
    """测试行业排名接口"""
    print("=" * 60)
    print("测试行业排名接口 (数据库版本)")
    print("=" * 60)
    
    # 1. 首次请求（数据库为空，应返回空数据）
    print("\n[测试 1] 首次请求 - 数据库无数据")
    response = requests.get(f"{BASE_URL}/api/fundamentals/industry/rank", timeout=10)
    print(f"状态码: {response.status_code}")
    data = response.json()
    print(f"返回数据: {data}")
    
    if data.get("data", {}).get("data"):
        print(f"✅ 已有数据，共 {len(data['data']['data'])} 个行业")
        print(f"Top 3: {[item['industry'] for item in data['data']['data'][:3]]}")
    else:
        print("⚠️  数据库无数据（预期行为）")
    
    print("\n" + "=" * 60)
    print("说明:")
    print("1. 如果返回空数据，这是正常的（首次访问）")
    print("2. 需要运行定时任务或手动触发预热来生成数据")
    print("3. 运行预热命令:")
    print("   docker exec data-service python -c \"from services.fundamentals_service import FundamentalsService; s=FundamentalsService(); s.calculate_industry_rank(force_recalculate=True)\"")
    print("=" * 60)

if __name__ == "__main__":
    test_industry_rank_api()
