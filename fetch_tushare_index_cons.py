import tushare as ts
from utils import connect_to_database
import pandas as pd
from datetime import datetime, timedelta
import time

# 由于tushare一次只能申请6000行数据，所以要分段获取
# 这里的token是临时token，只能使用到9/17日，遂不加密了

pro = ts.pro_api("59a28246427fde8f16d3b7e83b51d63bc9708ff2972d91777617c560")
engine = connect_to_database()

symbols = ["000300.SH", "000985.SH", "000852.SH", "000905.SH"]


# 定义时间分段函数
def get_date_ranges(start_date, end_date, max_days_per_request=20):
    """将时间范围分割成多个小段"""
    start = datetime.strptime(start_date, "%Y%m%d")
    end = datetime.strptime(end_date, "%Y%m%d")

    date_ranges = []
    current_start = start

    while current_start < end:
        current_end = min(current_start + timedelta(days=max_days_per_request), end)
        date_ranges.append(
            (current_start.strftime("%Y%m%d"), current_end.strftime("%Y%m%d"))
        )
        current_start = current_end + timedelta(days=1)

    return date_ranges


# 主循环
for symbol in symbols:
    print(f"正在处理指数: {symbol}")

    # 定义表名
    table_name = f"index_{symbol.replace('.SH', '')}_cons"

    # 获取时间分段
    date_ranges = get_date_ranges("20210101", "20250915")

    all_data = pd.DataFrame()

    for start_date, end_date in date_ranges:
        print(f"请求 {start_date} 到 {end_date} 的数据...")

        try:
            # 获取分段数据
            chunk_data = pro.index_weight(
                index_code=symbol, start_date=start_date, end_date=end_date
            )

            if not chunk_data.empty:
                chunk_data['con_code'] = chunk_data['con_code'].str.split('.').str[0]  # 去掉后缀
                chunk_data['index_code'] = chunk_data['index_code'].str.split('.').str[0]
                all_data = pd.concat([all_data, chunk_data], ignore_index=True)

            # 添加延迟以避免频繁请求
            time.sleep(0.5)

        except Exception as e:
            print(f"获取 {start_date} 到 {end_date} 的数据时出错: {e}")
            continue

    # 去重处理
    if not all_data.empty:
        # 检查表是否已存在
        try:
            existing_data = pd.read_sql_table(table_name, engine)
            # 合并新旧数据并去重
            combined_data = pd.concat([existing_data, all_data], ignore_index=True)
            combined_data = combined_data.drop_duplicates(
                subset=["trade_date", "con_code"], keep="last"
            ).reset_index(drop=True)
        except:
            # 表不存在，直接使用新数据
            combined_data = all_data.drop_duplicates(
                subset=["trade_date", "con_code"], keep="last"
            ).reset_index(drop=True)

        # 写入数据库
        combined_data["trade_date"] = pd.to_datetime(combined_data["trade_date"]).dt.date
        combined_data.to_sql(table_name, engine, if_exists="replace", index=False)

        # 打印统计信息
        combined_trade_dates = combined_data["trade_date"].unique()
        print(f"表 {table_name} 已更新，包含 {len(combined_trade_dates)} 个交易日的数据")
        print(f"最新交易日: {max(combined_trade_dates)}")
        print(f"总记录数: {len(combined_data)}")
    else:
        print(f"未能获取 {symbol} 的任何数据")

# 关闭连接
engine.dispose()
print("所有指数数据更新完成")
