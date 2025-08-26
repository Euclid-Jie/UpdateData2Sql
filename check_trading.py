from datetime import datetime
from zoneinfo import ZoneInfo


def get_trading_status() -> bool:
    """
    检查是否为中国A股交易日
    返回: 是否交易日: bool
    """
    cst_now = datetime.now(ZoneInfo("Asia/Shanghai"))
    today = cst_now.date()

    is_weekday = today.weekday() < 5
    is_holiday = False
    try:
        with open("Chinese_special_holiday.txt", "r") as f:
            holidays = {line.strip() for line in f}
        if today.strftime("%Y-%m-%d") in holidays:
            is_holiday = True
    except FileNotFoundError:
        pass

    return is_weekday and not is_holiday


# --- 主程序入口 ---
if __name__ == "__main__":
    # 仅在交易日返回True
    print(str(get_trading_status()).lower())
