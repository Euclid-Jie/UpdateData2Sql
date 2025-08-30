"""
日期处理工具模块
"""

import pandas as pd
from datetime import datetime, timedelta
from typing import List, Optional
from pathlib import Path


def load_holidays(holiday_path: str) -> List[str]:
    """加载节假日数据"""
    try:
        with open(holiday_path, 'r', encoding='utf-8') as f:
            holidays = [line.strip() for line in f if line.strip()]
        return holidays
    except FileNotFoundError:
        print(f"警告: 节假日文件 {holiday_path} 不存在")
        return []


def is_trading_day(date: str, holidays: List[str]) -> bool:
    """判断是否为交易日"""
    # 转换为datetime对象
    if isinstance(date, str):
        date_obj = pd.to_datetime(date)
    else:
        date_obj = date
    
    # 检查是否为周末
    if date_obj.weekday() >= 5:  # 周六、周日
        return False
    
    # 检查是否为节假日
    date_str = date_obj.strftime('%Y-%m-%d')
    if date_str in holidays:
        return False
    
    return True


def get_trading_dates(start_date: str, end_date: str, holidays: List[str]) -> List[str]:
    """获取指定日期范围内的交易日列表"""
    start = pd.to_datetime(start_date)
    end = pd.to_datetime(end_date)
    
    trading_dates = []
    current = start
    
    while current <= end:
        if is_trading_day(current, holidays):
            trading_dates.append(current.strftime('%Y-%m-%d'))
        current += timedelta(days=1)
    
    return trading_dates


def format_date(date, format_str: str = '%Y-%m-%d') -> str:
    """格式化日期"""
    if isinstance(date, str):
        date_obj = pd.to_datetime(date)
    else:
        date_obj = date
    
    return date_obj.strftime(format_str)


def get_latest_trading_date(holidays: List[str]) -> str:
    """获取最新的交易日"""
    today = datetime.now()
    
    # 如果今天是交易日，返回今天
    if is_trading_day(today, holidays):
        return today.strftime('%Y-%m-%d')
    
    # 否则返回最近的交易日
    current = today - timedelta(days=1)
    while not is_trading_day(current, holidays):
        current -= timedelta(days=1)
    
    return current.strftime('%Y-%m-%d')
