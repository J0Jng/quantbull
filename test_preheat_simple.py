"""简化版预热测试 - 只计算前3个行业"""
import sys
import os

# 添加路径
sys.path.insert(0, 'f:\\code\\项目\\quantbull\\data-service')
os.environ['PYTHONPATH'] = 'f:\\code\\项目\\quantbull\\data-service'

from services.fundamentals_service import FundamentalsService
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def test_simple_preheat():
    print("=" * 60)
    print("简化版预热测试")
    print("=" * 60)
    
    try:
        service = FundamentalsService()
        print("\n[1] 服务初始化成功")
        
        # 使用 force_recalculate=True 来触发计算
        print("\n[2] 开始计算（这可能需要几分钟）...")
        result = service.calculate_industry_rank(force_recalculate=True)
        
        print(f"\n[3] ✅ 计算完成！共 {len(result)} 个行业")
        
        if result:
            print(f"\n[4] 前5个行业:")
            for item in result[:5]:
                print(f"  - {item.industry}: 评分={item.score:.2f}, 排名={item.rank}")
        
        # 再次查询数据库验证持久化
        print("\n[5] 验证数据库持久化...")
        db_result = service.load_industry_rank_from_db("2026-01")
        print(f"  数据库中有 {len(db_result)} 条记录")
        
        if len(db_result) == len(result):
            print("  ✅ 数据已成功保存到数据库")
        else:
            print(f"  ⚠️  数据库记录数不匹配 ({len(db_result)} vs {len(result)})")
        
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_simple_preheat()
