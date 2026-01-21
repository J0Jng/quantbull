"""
东方财富网新闻抓取测试脚本

用于本地测试新闻抓取逻辑是否正常工作
"""
import asyncio
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from services.eastmoney_news_service import EastmoneyNewsAggregator


async def test_kuaixun_api():
    """测试快讯接口"""
    print("=" * 50)
    print("测试 1: 7×24 快讯接口")
    print("=" * 50)
    
    aggregator = EastmoneyNewsAggregator()
    
    import httpx
    async with httpx.AsyncClient() as client:
        items = await aggregator.fetch_kuaixun_news(client, limit=5)
        
    if items:
        print(f"成功获取 {len(items)} 条快讯:")
        for i, item in enumerate(items, 1):
            print(f"\n{i}. {item['title'][:50]}...")
            print(f"   ID: {item['id']}")
            print(f"   时间: {item['time']}")
            print(f"   摘要: {item.get('summary', '')[:50]}...")
            print(f"   链接: {item.get('url', 'N/A')}")
    else:
        print("快讯接口未返回数据")
    
    return len(items) > 0


async def test_category_news():
    """测试文章列表解析"""
    print("\n" + "=" * 50)
    print("测试 2: 财经频道文章列表")
    print("=" * 50)
    
    aggregator = EastmoneyNewsAggregator()
    
    import httpx
    async with httpx.AsyncClient() as client:
        category = {"name": "要闻", "url": "https://finance.eastmoney.com/a/cywjh.html"}
        items = await aggregator.fetch_category_news(category, client)
        
    if items:
        print(f"成功获取 {len(items)} 条文章:")
        for i, item in enumerate(items[:3], 1):
            print(f"\n{i}. {item['title'][:50]}...")
            print(f"   ID: {item['id']}")
            print(f"   时间: {item['time']}")
            print(f"   链接: {item.get('url', 'N/A')}")
            print(f"   图片: {item.get('img', 'N/A')}")
    else:
        print("文章列表解析未返回数据")
    
    return len(items) > 0


async def test_aggregate_news():
    """测试聚合接口"""
    print("\n" + "=" * 50)
    print("测试 3: 聚合新闻（完整流程）")
    print("=" * 50)
    
    aggregator = EastmoneyNewsAggregator()
    
    # 测试无关键词
    result = await aggregator.aggregate_news(limit=10)
    
    print(f"聚合结果:")
    print(f"  items 数量: {len(result['items'])}")
    print(f"  cached: {result['cached']}")
    print(f"  stale: {result['stale']}")
    print(f"  timestamp: {result['timestamp']}")
    
    if result['items']:
        print(f"\n前 3 条新闻:")
        for i, item in enumerate(result['items'][:3], 1):
            print(f"\n{i}. {item['title'][:50]}...")
            print(f"   来源: {item['source']}, 作者: {item.get('author', 'N/A')}")
    
    # 测试关键词过滤
    print("\n" + "-" * 30)
    print("测试关键词过滤: '股'")
    result_filtered = await aggregator.aggregate_news(limit=10, keyword="股")
    print(f"过滤后 items 数量: {len(result_filtered['items'])}")
    
    return len(result['items']) > 0


async def test_cache():
    """测试缓存机制"""
    print("\n" + "=" * 50)
    print("测试 4: 缓存机制")
    print("=" * 50)
    
    aggregator = EastmoneyNewsAggregator(cache_ttl=60)
    
    # 第一次请求
    result1 = await aggregator.aggregate_news(limit=5)
    print(f"第一次请求: cached={result1['cached']}")
    
    # 第二次请求（应该命中缓存）
    result2 = await aggregator.aggregate_news(limit=5)
    print(f"第二次请求: cached={result2['cached']}")
    
    return result1['cached'] == False and result2['cached'] == True


async def main():
    """运行所有测试"""
    print("东方财富网新闻抓取功能测试")
    print("=" * 60)
    
    tests = [
        ("快讯接口", test_kuaixun_api),
        ("文章列表", test_category_news),
        ("聚合新闻", test_aggregate_news),
        ("缓存机制", test_cache),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            success = await test_func()
            results.append((name, success))
        except Exception as e:
            print(f"\n❌ 测试 '{name}' 异常: {e}")
            results.append((name, False))
    
    # 汇总
    print("\n" + "=" * 60)
    print("测试汇总:")
    print("=" * 60)
    for name, success in results:
        status = "✅ 通过" if success else "❌ 失败"
        print(f"  {name}: {status}")
    
    passed = sum(1 for _, s in results if s)
    print(f"\n总计: {passed}/{len(results)} 测试通过")


if __name__ == "__main__":
    asyncio.run(main())
