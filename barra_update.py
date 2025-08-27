import sqlalchemy
import requests
import pandas as pd
import numpy as np
from sqlalchemy import text
from datetime import datetime
from config import HUOFUNIU_TOKEN
from utils import connect_to_database


def get_latest_date(engine, table_name):
    """从数据库获取该表数据的最新日期"""
    query = text(f"SELECT MAX(`日期`) as `latest_date` FROM `{table_name}`")
    try:
        latest_dates_df = pd.read_sql_query(query, engine)
        latest_dates_df["latest_date"] = pd.to_datetime(
            latest_dates_df["latest_date"]
        )  # 确保日期列是datetime类型
        print(f"成功从数据库中读取{table_name}的最新日期：")
        print(latest_dates_df)
    except Exception as e:
        print(f"读取数据库时发生错误: {e}")
    return latest_dates_df.iloc[0]["latest_date"]


def main():
    # 连接数据库
    engine = connect_to_database()
    today = datetime.now().date()
    today = np.datetime_as_string(np.datetime64(today), unit="D")
    url_dict = {
        "cne5": "https://pyapi.huofuniu.com/pyapi/factor/price?mod=cne5_style&sd={}&ed={}",
        "cne6": "https://pyapi.huofuniu.com/pyapi/factor/price?mod=cne6_style_new&sd={}&ed={}",
        "future": "https://pyapi.huofuniu.com/pyapi/factor/price?mod=future_new&plate=&sd={}&ed={}",
    }

    headers = {
        "access-token": HUOFUNIU_TOKEN,
    }
    for type, url in url_dict.items():
        latest_date = get_latest_date(engine, type)
        start_date = np.datetime_as_string(
            np.datetime64(latest_date) + np.timedelta64(1, "D"), unit="D"
        )
        print(f"Fetching data from {url.format(start_date, today)}")
        url = url.format(start_date, today)
        data = requests.get(url, headers=headers).json()["data"]
        all_data = pd.DataFrame()
        if len(data) == 0:
            print(f"没有需要更新的{type}的数据")
            continue
        for key, value in data.items():
            value = pd.DataFrame(value)
            value["日期"] = pd.to_datetime(value["date"])
            value.set_index("日期", inplace=True)
            value.rename(columns={"return": key}, inplace=True)
            value.drop(columns=["date"], inplace=True)
            all_data = pd.concat([all_data, value], axis=1)
        all_data.reset_index(drop=False, inplace=True)
        print(f"获取的{type}共有{len(all_data)}条数据")
        if all_data.empty:
            print(f"没有需要更新的{type}的数据")
        else:
            all_data.to_sql(
                name=type,
                con=engine,
                if_exists="append",
                index=False,
                dtype={"日期": sqlalchemy.types.Date},
            )
            print(f"数据已成功写入{type}表。")


if __name__ == "__main__":
    main()
