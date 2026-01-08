"""测试情绪分数数据库存取"""
import sys
import os

# 添加 data-service 到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'data-service'))

from datetime import datetime
from sqlmodel import select

# 必须在导入模型前先设置环境变量
os.environ['DATABASE_URL'] = 'postgresql+asyncpg://quantbull:change_me@localhost:5432/quantbull_db'
os.environ['SYNC_DATABASE_URL'] = 'postgresql://quantbull:change_me@localhost:5432/quantbull_db'

from core.database import SessionLocal, engine
from models.sentiment_score import SentimentScore
from models.hot_score import HotScore
from sqlmodel import SQLModel

def init_tables():
    """创建表"""
    print("正在创建表...")
    SQLModel.metadata.create_all(engine)
    print("✓ 表创建成功")

def test_sentiment_score():
    """测试情绪分数存取"""
    print("\n=== 测试情绪分数 ===")
    
    with SessionLocal() as session:
        # 插入测试数据
        test_data = SentimentScore(
            code="000001",
            trade_date="20260107",
            sentiment_score=0.75,
            discussion_volume=12345,
            hot_rank=25
        )
        session.add(test_data)
        session.commit()
        print("✓ 插入测试数据成功")
        
        # 查询数据
        statement = select(SentimentScore).where(
            SentimentScore.code == "000001",
            SentimentScore.trade_date == "20260107"
        )
        result = session.execute(statement).scalar_one_or_none()
        
        if result:
            print(f"✓ 查询成功: {result.code} - 情绪分数: {result.sentiment_score}")
            print(f"  讨论量: {result.discussion_volume}, 排名: {result.hot_rank}")
        else:
            print("✗ 查询失败")
        
        # 清理测试数据
        session.delete(result)
        session.commit()
        print("✓ 测试数据已清理")

def test_hot_score():
    """测试热点分数存取"""
    print("\n=== 测试热点分数 ===")
    
    with SessionLocal() as session:
        # 插入测试数据
        test_data = HotScore(
            code="000001",
            trade_date="20260107",
            hot_score=0.85,
            concept_score=0.5,
            limit_score=0.8,
            up_stat=3,
            concept_tags="芯片,人工智能,5G"
        )
        session.add(test_data)
        session.commit()
        print("✓ 插入测试数据成功")
        
        # 查询数据
        statement = select(HotScore).where(
            HotScore.code == "000001",
            HotScore.trade_date == "20260107"
        )
        result = session.execute(statement).scalar_one_or_none()
        
        if result:
            print(f"✓ 查询成功: {result.code} - 热点分数: {result.hot_score}")
            print(f"  概念分数: {result.concept_score}, 涨停分数: {result.limit_score}")
            print(f"  连板: {result.up_stat}天, 概念标签: {result.concept_tags}")
        else:
            print("✗ 查询失败")
        
        # 清理测试数据
        session.delete(result)
        session.commit()
        print("✓ 测试数据已清理")

def check_tables():
    """检查表是否存在"""
    print("\n=== 检查数据库表 ===")
    from sqlalchemy import inspect
    
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    
    if 'sentiment_score' in tables:
        print("✓ sentiment_score 表存在")
    else:
        print("✗ sentiment_score 表不存在")
    
    if 'hot_score' in tables:
        print("✓ hot_score 表存在")
    else:
        print("✗ hot_score 表不存在")
    
    print(f"\n所有表: {', '.join(tables)}")

if __name__ == "__main__":
    try:
        init_tables()
        check_tables()
        test_sentiment_score()
        test_hot_score()
        print("\n✓ 所有测试通过！")
    except Exception as e:
        print(f"\n✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
