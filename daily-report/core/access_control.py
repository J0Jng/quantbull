"""每日报告访问控制工具"""
from datetime import datetime, time
from zoneinfo import ZoneInfo


# 中国时区
CHINA_TZ = ZoneInfo("Asia/Shanghai")
# 访问截止时间（03:00）
ACCESS_CUTOFF_TIME = time(3, 0, 0)


def get_china_now() -> datetime:
    """获取中国时间的当前时间"""
    return datetime.now(CHINA_TZ)


def get_china_today() -> str:
    """获取中国时间的今天日期字符串 (YYYY-MM-DD)"""
    return get_china_now().date().isoformat()


def can_access_today_report(now: datetime = None) -> bool:
    """
    判断当前是否可以访问今天的报告
    
    规则：当天内参在次日 03:00 生成
    
    Args:
        now: 当前时间（用于测试），如果不提供则使用系统当前时间
        
    Returns:
        bool: True 表示可以访问，False 表示不可以
    """
    if now is None:
        now = get_china_now()
    else:
        # 确保传入的时间带有时区信息
        if now.tzinfo is None:
            now = now.replace(tzinfo=CHINA_TZ)
        else:
            now = now.astimezone(CHINA_TZ)
    
    # 判断当前时间是否 >= 03:00
    current_time = now.time()
    return current_time >= ACCESS_CUTOFF_TIME


def get_access_denied_message() -> str:
    """获取拒绝访问的提示信息"""
    return "当日内参在次日 03:00 生成，请查阅历史报告"
