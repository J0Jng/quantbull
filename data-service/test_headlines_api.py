"""
财经头条接口测试
用于验证 data-service 中新增的 headlines 接口功能
"""
import requests
import json

# 配置
BASE_URL = "http://localhost:8001"  # data-service 的直连地址
API_PREFIX = "/api/news"

def test_headlines_list():
    """测试获取财经头条列表接口"""
    url = f"{BASE_URL}{API_PREFIX}/headlines"
    
    print("\n=== 测试: 获取财经头条列表 ===")
    print(f"请求URL: {url}")
    
    # 测试基本列表查询
    response = requests.get(url, params={"page": 1, "page_size": 10})
    print(f"响应状态码: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"返回数据结构:")
        print(f"  - items 数量: {len(data.get('items', []))}")
        print(f"  - 当前页: {data.get('page')}")
        print(f"  - 每页条数: {data.get('page_size')}")
        print(f"  - 总数: {data.get('total')}")
        
        if data.get('items'):
            print(f"\n第一条新闻示例:")
            first_item = data['items'][0]
            print(f"  ID: {first_item.get('id')}")
            print(f"  标题: {first_item.get('title')}")
            print(f"  日期: {first_item.get('date')}")
            print(f"  摘要: {first_item.get('summary')[:50]}...")
            print(f"  标签: {first_item.get('tags')}")
    else:
        print(f"请求失败: {response.text}")
    
    # 测试关键词过滤
    print("\n--- 测试关键词过滤 ---")
    response = requests.get(url, params={"keyword": "央行", "page": 1, "page_size": 10})
    if response.status_code == 200:
        data = response.json()
        print(f"包含'央行'的新闻数量: {len(data.get('items', []))}")


def test_hot_headlines():
    """测试获取热点聚焦接口"""
    url = f"{BASE_URL}{API_PREFIX}/headlines/hot"
    
    print("\n=== 测试: 获取热点聚焦列表 ===")
    print(f"请求URL: {url}")
    
    response = requests.get(url, params={"limit": 8})
    print(f"响应状态码: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"返回热点数量: {len(data.get('items', []))}")
        
        if data.get('items'):
            print(f"\n热点新闻列表:")
            for idx, item in enumerate(data['items'], 1):
                print(f"  {idx}. [{item.get('id')}] {item.get('title')}")
    else:
        print(f"请求失败: {response.text}")


def test_headline_detail():
    """测试获取头条详情接口"""
    test_id = 1
    url = f"{BASE_URL}{API_PREFIX}/headlines/{test_id}"
    
    print(f"\n=== 测试: 获取头条详情 (ID={test_id}) ===")
    print(f"请求URL: {url}")
    
    response = requests.get(url)
    print(f"响应状态码: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"新闻详情:")
        print(f"  ID: {data.get('id')}")
        print(f"  标题: {data.get('title')}")
        print(f"  日期: {data.get('date')}")
        print(f"  摘要: {data.get('summary')}")
        print(f"  标签: {data.get('tags')}")
        print(f"  正文: {data.get('content', '(无)')}")
    else:
        print(f"请求失败: {response.text}")
    
    # 测试不存在的ID
    print(f"\n--- 测试不存在的ID ---")
    response = requests.get(f"{BASE_URL}{API_PREFIX}/headlines/999")
    print(f"响应状态码: {response.status_code}")
    if response.status_code == 404:
        print("正确返回 404")


if __name__ == "__main__":
    print("=" * 60)
    print("财经头条接口测试")
    print("=" * 60)
    print(f"\n请确保 data-service 正在运行 ({BASE_URL})")
    print("按 Enter 键开始测试，或 Ctrl+C 取消...")
    input()
    
    try:
        test_headlines_list()
        test_hot_headlines()
        test_headline_detail()
        
        print("\n" + "=" * 60)
        print("测试完成！")
        print("=" * 60)
    except requests.exceptions.ConnectionError:
        print(f"\n❌ 无法连接到 {BASE_URL}")
        print("请确保 data-service 已启动")
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
