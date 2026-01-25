"""测试每日报告15:30门禁逻辑"""
import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from datetime import datetime, time
from zoneinfo import ZoneInfo

from core.access_control import (
    can_access_today_report,
    get_china_now,
    get_china_today,
    get_access_denied_message,
    CHINA_TZ,
)


class TestAccessControl:
    """测试访问控制逻辑"""
    
    def test_can_access_before_cutoff(self):
        """测试15:30之前不能访问"""
        # 模拟 15:29
        test_time = datetime(2026, 1, 15, 15, 29, 0, tzinfo=CHINA_TZ)
        assert can_access_today_report(test_time) is False
        
    def test_can_access_at_cutoff(self):
        """测试15:30整点可以访问"""
        # 模拟 15:30
        test_time = datetime(2026, 1, 15, 15, 30, 0, tzinfo=CHINA_TZ)
        assert can_access_today_report(test_time) is True
        
    def test_can_access_after_cutoff(self):
        """测试15:30之后可以访问"""
        # 模拟 15:31
        test_time = datetime(2026, 1, 15, 15, 31, 0, tzinfo=CHINA_TZ)
        assert can_access_today_report(test_time) is True
        
        # 模拟 23:59
        test_time = datetime(2026, 1, 15, 23, 59, 0, tzinfo=CHINA_TZ)
        assert can_access_today_report(test_time) is True
    
    def test_get_china_today(self):
        """测试获取中国时区的今天"""
        today = get_china_today()
        # 应该返回 YYYY-MM-DD 格式
        assert len(today) == 10
        assert today[4] == '-'
        assert today[7] == '-'
    
    def test_access_denied_message(self):
        """测试拒绝访问消息"""
        message = get_access_denied_message()
        assert "15:30" in message
        assert len(message) > 0


if __name__ == "__main__":
    # 快速手动测试
    print("=" * 60)
    print("每日报告访问控制测试")
    print("=" * 60)
    
    # 当前时间
    now = get_china_now()
    print(f"\n当前中国时间: {now}")
    print(f"当前日期: {get_china_today()}")
    print(f"是否可以访问今日报告: {can_access_today_report()}")
    
    # 模拟不同时间点
    print("\n不同时间点的访问权限：")
    test_times = [
        (15, 29, "15:29"),
        (15, 30, "15:30"),
        (15, 31, "15:31"),
        (9, 0, "09:00"),
        (23, 59, "23:59"),
    ]
    
    for hour, minute, label in test_times:
        test_time = datetime(2026, 1, 15, hour, minute, 0, tzinfo=CHINA_TZ)
        can_access = can_access_today_report(test_time)
        status = "✓ 可以访问" if can_access else "✗ 不能访问"
        print(f"  {label}: {status}")
    
    print(f"\n拒绝访问消息: {get_access_denied_message()}")
    print("=" * 60)
