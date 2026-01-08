#!/usr/bin/env python
"""测试 industry/rank 接口"""
import requests
import sys

url = "http://localhost:8001/api/fundamentals/industry/rank"

try:
    print(f"测试接口: {url}")
    response = requests.get(url, timeout=10)
    print(f"状态码: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"月份: {data.get('month')}")
        print(f"行业数量: {len(data.get('data', []))}")
        
        if data.get('data'):
            print("\n前5个行业:")
            for item in data['data'][:5]:
                print(f"  {item['rank']}. {item['industry']} - 分数: {item['score']}")
    else:
        print(f"错误: {response.text}")
        
except requests.exceptions.Timeout:
    print("请求超时（10秒）")
    sys.exit(1)
except Exception as e:
    print(f"异常: {e}")
    sys.exit(1)
