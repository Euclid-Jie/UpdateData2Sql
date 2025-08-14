import sys
from datetime import datetime, time
from zoneinfo import ZoneInfo
from typing import NamedTuple, List, Tuple


class TimeInterval(NamedTuple):
    start: int  # 开始时间（小时分钟）
    end: int  # 结束时间（小时分钟）


def get_trading_status(
    time_interval: list[TimeInterval] = [
        TimeInterval(930, 1130),
        TimeInterval(1300, 1500),
    ]
) -> Tuple[bool, bool]:
    """
    检查是否为中国A股交易日和交易时间。
    返回: 元组 (是否交易日: bool, 是否交易时间: bool)
    """
    cst_now = datetime.now(ZoneInfo("Asia/Shanghai"))
    today = cst_now.date()
    current_time = cst_now.time()

    is_weekday = today.weekday() < 5
    is_holiday = False
    try:
        with open("Chinese_special_holiday.txt", "r") as f:
            holidays = {line.strip() for line in f}
        if today.strftime("%Y-%m-%d") in holidays:
            is_holiday = True
    except FileNotFoundError:
        pass

    is_trading_day = is_weekday and not is_holiday

    if not is_trading_day:
        return False, False

    is_trading_time = False
    for interval in time_interval:
        start_time = time(hour=interval.start // 100, minute=interval.start % 100)
        end_time = time(hour=interval.end // 100, minute=interval.end % 100)
        if start_time <= current_time <= end_time:
            is_trading_time = True
            break

    return is_trading_day, is_trading_time


# --- 主程序入口 ---
if __name__ == "__main__":
    # 默认检查模式为 'day_and_time'
    check_mode = "day_and_time"

    # 从命令行参数判断是否切换为只检查日期的模式
    if len(sys.argv) > 1 and sys.argv[1] == "--check-day-only":
        check_mode = "day_only"

    time_interval = [
        TimeInterval(700, 800),  # 7:00 - 8:00
    ]
    is_day, is_time = get_trading_status(time_interval)
    should_run = False

    # 根据检查模式决定最终结果
    if check_mode == "day_only":
        # 如果模式是只检查日期，那么只要是交易日就应该运行
        if is_day:
            should_run = True
    else:  # 默认模式 'day_and_time'
        # 如果是默认模式，则需要日期和时间都满足
        if is_day and is_time:
            should_run = True

    # 将最终的布尔结果转换为小写的字符串 'true' 或 'false' 并打印
    print(str(should_run).lower())
