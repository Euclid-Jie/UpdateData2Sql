import akshare as ak
import pandas as pd
import sqlalchemy
import requests
import chinese_calendar
from sqlalchemy import text
from datetime import datetime, timedelta
from config import SQL_PASSWORDS, SQL_HOST

print("连接到数据库...")

# 数据库连接
engine = sqlalchemy.create_engine("mysql+pymysql://dev:{SQL_PASSWORDS}@{SQL_HOST}:3306/UpdatedData?charset=utf8")
# engine = sqlalchemy.create_engine("mysql+pymysql:// /intern?charset=utf8mb4")
table_name = "bench_basic_data"
query =text(f"SELECT `code`, MAX(`date`) as `latest_date` FROM `{table_name}` GROUP BY `code`")

try:
    latest_dates_df = pd.read_sql_query(query, engine)
    latest_dates_df['latest_date'] = pd.to_datetime(latest_dates_df['latest_date']) # 确保日期列是datetime类型
    print("成功从数据库中读取每个代码的最新日期：")
    print(latest_dates_df)
except Exception as e:
    print(f"读取数据库时发生错误: {e}")
    print("可能是第一次运行或表不存在。将创建一个空的DataFrame继续。")
    latest_dates_df = pd.DataFrame(columns=['code', 'latest_date'])

today_str = datetime.now().strftime("%Y%m%d")


# akshare下的指数
print("\n--- 开始处理 akshare 指数数据 ---")
symbols = {"000016.SH": "sh000016", "000852.SH": "sh000852", "000905.SH": "sh000905"}
all_new_data = []

latest_dates_dict = latest_dates_df.set_index('code')['latest_date'].to_dict()

for code_db, code_ak in symbols.items():
    print(f"\n>>> 正在处理代码: {code_db}")
    latest_date = latest_dates_dict.get(code_db)
    start_date = (latest_date + timedelta(days=1)).strftime("%Y%m%d")
    print(f"数据库中最新日期为: {latest_date.date()}, 将从 {start_date} 开始获取。")

    if start_date > today_str:
        print("数据已是最新，无需更新。")
        continue

    try:
        # 【重要】注意这里的 symbol 参数用的是字典的 value
        daily_df = ak.stock_zh_a_daily(symbol=code_ak, start_date=latest_date, end_date=today_str)
        daily_df['date'] = pd.to_datetime(daily_df['date']) # 确保date列是datetime类型

        if daily_df.empty:
            print("在指定日期范围内未获取到新数据。")
            continue
        print(f"成功获取 {len(daily_df)-1} 条新数据，额外获取了一条当天数据用于计算涨跌幅")

        # 数据清洗和处理
        data = daily_df[["date", "open", "high", "low", "close", "volume", "amount"]].copy() # 使用 .copy() 避免 SettingWithCopyWarning
        data.rename(columns={
                "open": "OPEN", "high": "HIGH", "low": "LOW",
                "close": "CLOSE", "volume": "VOLUME", "amount": "AMT",
            }, inplace=True)

        data["PCT_CHG"] = data["CLOSE"].pct_change() * 100
        data['code'] = code_db # 插入用于识别代码的列
        data = data[data['date'] >= start_date]  # 只保留需要的日期范围
        print(f"处理后剩余 {len(data)} 条新数据。")

        all_new_data.append(data)

    except Exception as e:
        print(f"通过 akshare 获取代码 {code_ak} 数据时出错: {e}")


# wind指数数据
print("\n--- 开始处理 Wind 指数数据 ---")
indexes = {"868008.WI": "6644c422b6edae80b3c7a7d55803bc9e", "8841425.WI": "e2d5a98547c3ee7c923a0259cee963e4"}
for index_code, index_id in indexes.items():
    print(f"\n>>> 正在处理代码: {index_code}")
    url = f"https://indexapi.wind.com.cn/indicesWebsite/api/Kline?indexId={index_id}&period=1Y&lan=cn"
    res = requests.get(url)
    data = pd.DataFrame(res.json()["Result"]["data"])
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
    latest_date = latest_dates_dict.get(index_code)
    start_date = (latest_date + timedelta(days=1)).strftime("%Y%m%d")
    if start_date > today_str:
        print("数据已是最新，无需更新。")
        continue
    new_data = data[data["date"] >= start_date]
    new_data['code'] = index_code # 插入用于识别代码的列
    print(f"成功获取 {len(new_data)} 条新数据。")
    all_new_data.append(new_data)

# 中证数据
print("\n--- 开始处理 中证 指数数据 ---")

codes = {"000985.CSI": "000985", "932000.CSI": "932000", "000300.SH":"000300"}

for code, code_csi in codes.items():
    print(f"\n>>> 正在处理代码: {code}")
    latest_date = latest_dates_dict.get(code)
    start_date = (latest_date + timedelta(days=1)).strftime("%Y%m%d")
    if start_date > today_str:
        print("数据已是最新，无需更新。")
        continue
    print(f"数据库中最新日期为: {latest_date.date()}, 将从 {start_date} 开始获取。")
    url = f"https://www.csindex.com.cn/csindex-home/perf/index-perf?indexCode={code_csi}&startDate={start_date}&endDate={today_str}"
    res = requests.get(url)
    data = res.json()["data"]
    data = pd.DataFrame(data)[["tradeDate", "open", "high", "low", "close", "tradingVol", "tradingValue","changePct"]]
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
    all_new_data.append(data)

print("\n--- 写入数据库 ---")

#检查数据是否有非交易日数据
def is_trading_day(date):
    return chinese_calendar.is_workday(date)

if all_new_data:
    final_df = pd.concat(all_new_data, ignore_index=True)
    mask = final_df['date'].apply(is_trading_day)
    final_df = final_df[mask]
    print(f"过滤后，剩余 {len(final_df)} 条交易日数据。")
    # 转换日期列为datetime对象，以确保与数据库兼容
    final_df['date'] = pd.to_datetime(final_df['date'])

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