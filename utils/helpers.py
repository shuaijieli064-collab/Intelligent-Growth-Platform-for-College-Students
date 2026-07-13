"""通用工具函数."""
import random
from datetime import date, datetime, timedelta


def random_date(start: date, end: date) -> date:
    """生成 [start, end] 范围内的随机日期."""
    delta = (end - start).days
    return start + timedelta(days=random.randint(0, delta))


def clamp(value: float, lo: float = 0.0, hi: float = 100.0) -> float:
    """将值限制在[lo, hi]区间内."""
    return max(lo, min(hi, value))


def weighted_average(values: list[float], weights: list[float]) -> float:
    """加权平均."""
    if len(values) != len(weights) or sum(weights) == 0:
        return 0.0
    return sum(v * w for v, w in zip(values, weights)) / sum(weights)


def format_percent(value: float) -> str:
    """格式化百分比."""
    return f"{value:.1f}%"


def today_str() -> str:
    """今天的日期字符串."""
    return date.today().isoformat()


def now_str() -> str:
    """当前时间字符串."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
