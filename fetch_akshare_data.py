import pandas as pd
from datetime import datetime
from utils import (
    connect_to_database,
    load_holidays,
    get_latest_dates,
    update_latest_dates,
    get_source_info,
    fetch_akshare_data,
    save_data_to_database,
)

# --- 函数定义 ---
# 删除原有的 update_latest_dates、get_source_info、fetch_akshare_data 和 save_data_to_database 函数


# ==============================================================================
#                               主程序入口
# ==============================================================================
def main():
    """程序的主执行函数"""
    # 判断交易日，决定是否运行
    holiday_path = "Chinese_special_holiday.txt"
    holidays = load_holidays(holiday_path)

    # 定义表名
    table_name = "stock_basic_data_ak"
    info_name = "stock_info_ak"

    # 执行数据处理流程
    engine = connect_to_database()
    latest_dates_df = get_latest_dates(engine, table_name)
    update_latest_dates(engine, latest_dates_df, info_name)
    info_df = get_source_info(engine, info_name)
    info_df["updated_date"] = pd.to_datetime(info_df["updated_date"])

    # 创建查询表
    symbols_ak = {
        row["code"]: row["code"][-2:].lower() + row["code"][0:6]
        for _, row in info_df.iterrows()
    }

    # 打印获取到的指数代码信息，与原始脚本行为保持一致
    print("获取到的指数代码信息：")
    print("akshare:", symbols_ak)

    # 初始化数据列表和日期
    all_new_data = []
    today_str = datetime.now().strftime("%Y%m%d")
    latest_dates_dict = info_df.set_index("code")["updated_date"].to_dict()

    # 从各数据源获取数据
    all_new_data.extend(fetch_akshare_data(symbols_ak, latest_dates_dict, today_str))
    all_new_data = [df for df in all_new_data if not df.empty]

    # 保存数据到数据库
    save_data_to_database(all_new_data, table_name, engine, holidays)
    # 最后再更新一遍最新日期，确保bench_info_wind表中的日期是最新的
    latest_dates_df = get_latest_dates(engine, table_name)
    update_latest_dates(engine, latest_dates_df, info_name)


# 当该脚本被直接执行时，调用main()函数
if __name__ == "__main__":
    main()
