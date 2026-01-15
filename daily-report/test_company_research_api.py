"""测试公司研报 API"""
import asyncio
import httpx


async def test_api():
    """测试公司研报接口"""
    base_url = "http://localhost:8004"
    
    print("=" * 60)
    print("测试公司研报 API")
    print("=" * 60)
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        # 1. 测试查询列表（应该返回空列表）
        print("\n1. 测试查询研报列表...")
        try:
            response = await client.get(f"{base_url}/company-research/reports")
            print(f"状态码: {response.status_code}")
            print(f"响应: {response.json()}")
        except Exception as e:
            print(f"错误: {e}")
        
        # 2. 测试生成研报
        print("\n2. 测试生成研报...")
        try:
            data = {
                "company_name": "测试公司",
                "stock_code": "000001",
                "rating": "buy",
                "report_type": "summary",
                "include_risks": True,
                "company_info": "这是一家测试公司，主要业务是测试。",
                "tags": ["测试", "示例"],
                "force": False
            }
            response = await client.post(
                f"{base_url}/company-research/reports/generate",
                json=data
            )
            print(f"状态码: {response.status_code}")
            result = response.json()
            print(f"响应: {result}")
            
            if result.get("code") == 0:
                report_id = result.get("data", {}).get("id")
                print(f"\n✅ 研报生成成功，ID: {report_id}")
                
                # 3. 测试查询详情
                if report_id:
                    print(f"\n3. 测试查询研报详情 (ID={report_id})...")
                    try:
                        response = await client.get(
                            f"{base_url}/company-research/reports/{report_id}"
                        )
                        print(f"状态码: {response.status_code}")
                        detail = response.json()
                        print(f"公司名称: {detail.get('data', {}).get('company_name')}")
                        print(f"评级: {detail.get('data', {}).get('rating')}")
                        print(f"研报内容长度: {len(detail.get('data', {}).get('report_content', ''))}")
                    except Exception as e:
                        print(f"错误: {e}")
                
                # 4. 再次查询列表（应该有1条记录）
                print(f"\n4. 再次查询研报列表...")
                try:
                    response = await client.get(f"{base_url}/company-research/reports")
                    print(f"状态码: {response.status_code}")
                    result = response.json()
                    total = result.get("data", {}).get("total", 0)
                    items = result.get("data", {}).get("items", [])
                    print(f"总数: {total}")
                    print(f"列表长度: {len(items)}")
                    if items:
                        print(f"第一条记录: {items[0].get('company_name')} - {items[0].get('rating')}")
                except Exception as e:
                    print(f"错误: {e}")
        except Exception as e:
            print(f"错误: {e}")
    
    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(test_api())
