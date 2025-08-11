import akshare as ak
import pandas as pd
import numpy as np
import sqlalchemy
import requests
from sqlalchemy import text
from datetime import datetime, timedelta
from config import SQL_PASSWORDS, SQL_HOST

# --- 函数定义 ---

def load_holidays(filepath: str) -> list[str]:
    """
    一次性从文件中加载并清理节假日数据。
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        holidays = [
            line.strip() for line in f
            if line.strip() and not line.startswith('#')
        ]
    return holidays

def is_trading(date, holidays):
    """检查给定日期是否为交易日"""
    is_trading = np.is_busday(date, holidays=holidays)
    return is_trading

def connect_to_database():
    """创建并返回数据库引擎"""
    print("连接到数据库...")
    # 数据库连接
    # engine = sqlalchemy.create_engine(f"mysql+pymysql://dev:{SQL_PASSWORDS}@{SQL_HOST}:3306/UpdatedData?charset=utf8")
    return engine

def get_latest_dates(engine, table_name):
    """从数据库获取每个代码的最新日期"""
    query = text(f"SELECT `code`, MAX(`date`) as `latest_date` FROM `{table_name}` GROUP BY `code`")
    try:
        latest_dates_df = pd.read_sql_query(query, engine)
        latest_dates_df['latest_date'] = pd.to_datetime(latest_dates_df['latest_date']) # 确保日期列是datetime类型
        print("成功从数据库中读取每个代码的最新日期：")
        print(latest_dates_df)
    except Exception as e:
        print(f"读取数据库时发生错误: {e}")
        print("可能是第一次运行或表不存在。将创建一个空的DataFrame继续。")
        latest_dates_df = pd.DataFrame(columns=['code', 'latest_date'])
    return latest_dates_df

def get_source_info(engine, info_name):
    """读取数据获取的参数信息"""
    info_query = text(f"SELECT code, indexID, source FROM {info_name}")
    info_df = pd.read_sql_query(info_query, engine)
    return info_df

def fetch_akshare_data(symbols_ak, latest_dates_dict, today_str):
    """处理并从akshare获取指数数据"""
    print("\n--- 开始处理 akshare 指数数据 ---")
    data_list = []
    for code_db, code_ak in symbols_ak.items():
        print(f"\n>>> 正在处理代码: {code_db}")
        latest_date = latest_dates_dict.get(code_db)
        if not latest_date:
            print(f"警告: 在数据库中未找到代码 {code_db} 的最新日期，跳过。")
            continue

        start_date = (latest_date + timedelta(days=1)).strftime("%Y%m%d")
        print(f"数据库中最新日期为: {latest_date.date()}, 将从 {start_date} 开始获取。")

        if start_date > today_str:
            print("数据已是最新，无需更新。")
            continue

        try:
            # 【重要】注意这里的 symbol 参数用的是字典的 value
            # 传入latest_date对象，akshare会处理
            # 判断latest_date是否为周一，若是周一，check_date为上周五
            if latest_date.weekday() == 0:
                check_date = (latest_date - timedelta(days=3)).strftime("%Y%m%d") # akshare如果start或者end为周末，会有数据填充，如果周末包含在区间内则会自动删除
            else:
                check_date = latest_date.strftime("%Y%m%d")
            daily_df = ak.stock_zh_a_daily(symbol=code_ak, start_date=check_date, end_date=today_str)
            daily_df['date'] = pd.to_datetime(daily_df['date']) # 确保date列是datetime类型

            if daily_df.empty:
                print("在指定日期范围内未获取到新数据。")
                continue

            print(f"成功获取 {len(daily_df)} 条数据，额外获取了用于计算涨跌幅的数据")

            # 数据清洗和处理
            data = daily_df[["date", "open", "high", "low", "close", "volume", "amount"]].copy() # 使用 .copy() 避免 SettingWithCopyWarning
            data.rename(columns={
                    "open": "OPEN", "high": "HIGH", "low": "LOW",
                    "close": "CLOSE", "volume": "VOLUME", "amount": "AMT",
                }, inplace=True)

            data["PCT_CHG"] = data["CLOSE"].pct_change() * 100
            data['code'] = code_db # 插入用于识别代码的列
            # 确保使用datetime对象进行比较，以保证准确性
            data = data[data['date'] >= pd.to_datetime(start_date)]
            print(f"处理后剩余 {len(data)} 条新数据。")

            data_list.append(data)

        except Exception as e:
            print(f"通过 akshare 获取代码 {code_ak} 数据时出错: {e}")
    return data_list

def fetch_wind_data(symbols_wind, latest_dates_dict, today_str):
    """处理并从Wind获取指数数据"""
    print("\n--- 开始处理 Wind 指数数据 ---")
    data_list = []
    for index_code, index_id in symbols_wind.items():
        print(f"\n>>> 正在处理代码: {index_code}")
        latest_date = latest_dates_dict.get(index_code)
        if not latest_date:
            print(f"警告: 在数据库中未找到代码 {index_code} 的最新日期，跳过。")
            continue

        start_date = (latest_date + timedelta(days=1)).strftime("%Y%m%d")
        if start_date > today_str:
            print("数据已是最新，无需更新。")
            continue

        try:
            url = f"https://indexapi.wind.com.cn/indicesWebsite/api/Kline?indexId={index_id}&period=1Y&lan=cn"
            res = requests.get(url)
            data_json = res.json()
            # 检查返回结果是否有效
            if not data_json.get("Result") or not data_json["Result"].get("data"):
                 print(f"Wind API 未返回代码 {index_code} 的有效数据。")
                 continue

            data = pd.DataFrame(data_json["Result"]["data"])
            data = data[["tradeDate", "open", "hight", "low", "close", "pctChange", "volume", "amount"]]
            data = data.rename(
                                columns={
                                "tradeDate": "date",
                                "open": "OPEN",
                                "hight": "HIGH",
                                "low": "LOW",
                                "close": "CLOSE",
                                "pctChange": "PCT_CHG",
                                "volume": "VOLUME",
                                "amount": "AMT"
                                }
                            )
            data["date"] = pd.to_datetime(data["date"], format="%Y%m%d")

            new_data = data[data["date"] >= pd.to_datetime(start_date)].copy() # 使用.copy()避免警告
            new_data['code'] = index_code # 插入用于识别代码的列
            print(f"成功获取 {len(new_data)} 条新数据。")
            data_list.append(new_data)
        except Exception as e:
            print(f"处理 Wind 代码 {index_code} 时出错: {e}")
    return data_list

def fetch_csi_data(symbols_csi, latest_dates_dict, today_str):
    """处理并从中证获取指数数据"""
    print("\n--- 开始处理 中证 指数数据 ---")
    data_list = []
    for code, code_csi in symbols_csi.items():
        print(f"\n>>> 正在处理代码: {code}")
        latest_date = latest_dates_dict.get(code)
        if not latest_date:
            print(f"警告: 在数据库中未找到代码 {code} 的最新日期，跳过。")
            continue

        start_date = (latest_date + timedelta(days=1)).strftime("%Y%m%d")
        if start_date > today_str:
            print("数据已是最新，无需更新。")
            continue
        print(f"数据库中最新日期为: {latest_date.date()}, 将从 {start_date} 开始获取。")

        try:
            url = f"https://www.csindex.com.cn/csindex-home/perf/index-perf?indexCode={code_csi}&startDate={start_date}&endDate={today_str}"
            res = requests.get(url)
            data_json = res.json()
            if not data_json.get("data"):
                print("中证 API 未返回有效数据。")
                continue

            data = pd.DataFrame(data_json["data"])[["tradeDate", "open", "high", "low", "close", "tradingVol", "tradingValue","changePct"]]
            data = data.rename(
                columns={
                    "tradeDate": "date",
                    "open": "OPEN",
                    "high": "HIGH",
                    "low": "LOW",
                    "close": "CLOSE",
                    "tradingVol": "VOLUME",
                    "tradingValue": "AMT",
                    "changePct": "PCT_CHG"
                }
            )
            data["code"] = code # 插入用于识别代码的列
            data["date"] = pd.to_datetime(data["date"])
            print(f"成功获取 {len(data)} 条新数据。")
            data_list.append(data)
        except Exception as e:
            print(f"处理中证代码 {code} 时出错: {e}")
    return data_list

def save_data_to_database(all_new_data, table_name, engine, holidays):
    """合并数据，过滤并写入数据库"""
    print("\n--- 写入数据库 ---")

    if all_new_data:
        final_df = pd.concat(all_new_data, ignore_index=True)
        final_df['date'] = pd.to_datetime(final_df['date']).dt.date  # 确保date列是日期类型
        mask = final_df['date'].apply(lambda d: is_trading(d, holidays))
        final_df = final_df[mask]
        print(f"过滤后，剩余 {len(final_df)} 条交易日数据。")

        print(f"总计 {len(final_df)} 条新数据将被写入数据库。")

        try:
            final_df.to_sql(
                name=table_name,
                con=engine,
                if_exists='append',
                index=False,
                dtype={'date': sqlalchemy.types.Date} # 明确指定date列的类型
            )
            print("\n数据成功写入数据库！")
        except Exception as e:
            print(f"\n数据写入数据库时发生错误: {e}")
    else:
        print("\n任务完成，没有新数据需要写入数据库。")

# ==============================================================================
#                               主程序入口
# ==============================================================================
def main():
    """程序的主执行函数"""
    # 判断交易日，决定是否运行
    holiday_path = "Chinese_special_holiday.txt"
    holidays = load_holidays(holiday_path)
    today = datetime.now().date()
    if not is_trading(today, holidays):
        print(f"今天 {today} 不是交易日，程序终止。")
        return
    print(f"今天 {today} 是交易日，程序继续执行。")

    # 定义表名
    table_name = "bench_basic_data"
    info_name = "bench_info_wind"

    # 执行数据处理流程
    engine = connect_to_database()
    latest_dates_df = get_latest_dates(engine, table_name)
    info_df = get_source_info(engine, info_name)

    # 创建查询表
    symbols_ak = {} # symbols = {"000016.SH": "sh000016", "000852.SH": "sh000852", "000905.SH": "sh000905"}
    symbols_wind = {} # indexes = {"868008.WI": "6644c422b6edae80b3c7a7d55803bc9e", "8841425.WI": "e2d5a98547c3ee7c923a0259cee963e4"}
    symbols_csi = {}#codes = {"000985.CSI": "000985", "932000.CSI": "932000", "000300.SH":"000300"}

    # 遍历info_df，填充symbols_ak, symbols_wind, symbols_csi
    for index, row in info_df.iterrows():
        if row['source'] == 'ak':
            symbols_ak[row['code']] = "sh" +row['code'][0:6]
        elif row['source'] == 'wind':
            symbols_wind[row['code']] = row['indexID']
        elif row['source'] == 'CSI':
            symbols_csi[row['code']] = row['code'][0:6]

    # 打印获取到的指数代码信息，与原始脚本行为保持一致
    print("获取到的指数代码信息：")
    print("akshare:", symbols_ak)
    print("wind:", symbols_wind)
    print("中证:", symbols_csi)

    # 初始化数据列表和日期
    all_new_data = []
    today_str = datetime.now().strftime("%Y%m%d")
    latest_dates_dict = latest_dates_df.set_index('code')['latest_date'].to_dict()

    # 从各数据源获取数据
    all_new_data.extend(fetch_akshare_data(symbols_ak, latest_dates_dict, today_str))
    all_new_data.extend(fetch_wind_data(symbols_wind, latest_dates_dict, today_str))
    all_new_data.extend(fetch_csi_data(symbols_csi, latest_dates_dict, today_str))

    # 保存数据到数据库
    save_data_to_database(all_new_data, table_name, engine, holidays)


# 当该脚本被直接执行时，调用main()函数
if __name__ == "__main__":
    main()