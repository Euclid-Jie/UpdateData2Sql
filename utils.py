from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
from pathlib import Path
import requests
from typing import Literal, Tuple
from datetime import datetime, timedelta
import re
import urllib.parse
import json
import uuid
import time
import sqlalchemy
from config import SQL_PASSWORDS, SQL_HOST
from sqlalchemy.sql import text
import akshare as ak


def connect_to_database():
    """创建并返回数据库引擎"""
    print("连接到数据库...")
    # 数据库连接
    engine = sqlalchemy.create_engine(
        f"mysql+pymysql://dev:{SQL_PASSWORDS}@{SQL_HOST}:3306/UpdatedData?charset=utf8"
    )
    return engine


def update_loc_method(
    engine: sqlalchemy.engine.Engine,
    table_name: str = "pfund_info",
    key: str = "序号",
    var: str = "净值截至时间",
    data: dict = {666: "2001-06-06"},
    debug: bool = False,
):
    """
    注意data中的value在table中必须是字符串类型, 而且key必须是int类型

    """
    with engine.connect() as conn:
        with conn.begin():  # 开启事务
            for k, v in data.items():
                sql_text = f"UPDATE {table_name} SET {var} = '{v}' WHERE {key} = '{k}'"
                res = conn.execute(sqlalchemy.text(sql_text))
                if debug:
                    print(f"Executing SQL: {sql_text}")
                    print(
                        f"Updated {var} with {v} Where {key} = {k} , affected rows: {res.rowcount}"
                    )


def get_single_company_fund_info(
    keyword: str = "", begin_date: str = "2025-06-15"
) -> pd.DataFrame:
    page = 0
    size = 100
    totalElements = 100
    all_data_df = pd.DataFrame()
    data_json = {
        # "establishDateQuery": {"from": "2025-01-01", "to": "9999-01-01"},
        "putOnRecordDate": {"from": begin_date, "to": "9999-01-01"},
        "keyword": keyword,
    }
    while totalElements > page * size:
        res = _get_fund_info(page, data_json)
        try:
            totalElements = res.json()["totalElements"]
        except:
            return pd.DataFrame()  # 如果没有数据，返回空DataFrame
        data = pd.DataFrame(res.json()["content"])
        if len(data) == 0:
            print("No more data found in {} page {}".format(keyword, page + 1))
            break
        data["putOnRecordDate"] = data["putOnRecordDate"].apply(
            lambda x: time.strftime("%Y-%m-%d", time.localtime(x / 1000))
        )
        data["establishDate"] = data["establishDate"].apply(
            lambda x: time.strftime("%Y-%m-%d", time.localtime(x / 1000))
        )
        all_data_df = pd.concat([all_data_df, data], ignore_index=True)
        print(f"Processing page {page + 1}, total elements: {totalElements}")
        page += 1
    return all_data_df


def _get_fund_info(page, data_json):
    res = requests.post(
        "https://gs.amac.org.cn/amac-infodisc/api/pof/fund?",
        params={"page": page, "size": 100},
        json=data_json,
    )
    return res


def get_company_base_info(keyword):
    page = 0
    size = 100
    totalElements = 100
    all_data_df = pd.DataFrame()
    data_json = {
        "keyword": keyword,
    }
    while totalElements > page * size:
        res = _get_company_base_info(page, data_json)
        totalElements = res.json()["numberOfElements"]
        data = pd.DataFrame(res.json()["content"])
        if len(data) == 0:
            print("No more data found in {} page {}".format(keyword, page + 1))
            break
        data["registerDate"] = data["registerDate"].apply(
            lambda x: time.strftime("%Y-%m-%d", time.localtime(x / 1000))
        )
        data["establishDate"] = data["establishDate"].apply(
            lambda x: time.strftime("%Y-%m-%d", time.localtime(x / 1000))
        )
        all_data_df = pd.concat([all_data_df, data], ignore_index=True)
        page += 1
    return all_data_df


def _get_company_base_info(page, data_json):
    res = requests.post(
        "https://gs.amac.org.cn/amac-infodisc/api/pof/manager/query",
        params={"page": page, "size": 100},
        json=data_json,
    )
    return res


def load_bais(type=Literal["IF", "IC", "IM", "IH"]) -> pd.DataFrame:
    if type == "IF":
        data = "params=%7B%22head%22%3A%22IF%22%2C%22N%22%3A251%7D&PageID=46803&websiteID=20906&ContentID=Content&UserID=&menup=0&_cb=&_cbdata=&_cbExec=1&_cbDispType=1&__pageState=0&__globalUrlParam=%7B%22PageID%22%3A%2246803%22%2C%22pageid%22%3A%2246803%22%7D&g_randomid=randomid_1051095574548506702800710985&np=%5B%2246803%40Content%40TwebCom_div_1_0%40220907102451613%22%5D&modename=amljaGFfZGFpbHlfY2hhcnRfN0Q5MTQ5NDE%3D&creator=cjzq"
    elif type == "IC":
        data = "params=%7B%22head%22%3A%22IC%22%2C%22N%22%3A251%7D&PageID=46803&websiteID=20906&ContentID=Content&UserID=&menup=0&_cb=&_cbdata=&_cbExec=1&_cbDispType=1&__pageState=0&__globalUrlParam=%7B%22PageID%22%3A%2246803%22%2C%22pageid%22%3A%2246803%22%7D&g_randomid=randomid_1051095574548506702800710985&np=%5B%2246803%40Content%40TwebCom_div_1_0%40220907102451613%22%5D&modename=amljaGFfZGFpbHlfY2hhcnRfN0Q5MTQ5NDE%3D&creator=cjzq"
    elif type == "IM":
        data = "params=%7B%22head%22%3A%22IM%22%2C%22N%22%3A251%7D&PageID=46803&websiteID=20906&ContentID=Content&UserID=&menup=0&_cb=&_cbdata=&_cbExec=1&_cbDispType=1&__pageState=0&__globalUrlParam=%7B%22PageID%22%3A%2246803%22%2C%22pageid%22%3A%2246803%22%7D&g_randomid=randomid_1051095574548506702800710985&np=%5B%2246803%40Content%40TwebCom_div_1_0%40220907102451613%22%5D&modename=amljaGFfZGFpbHlfY2hhcnRfN0Q5MTQ5NDE%3D&creator=cjzq"
    elif type == "IH":
        data = "params=%7B%22head%22%3A%22IH%22%2C%22N%22%3A251%7D&PageID=46803&websiteID=20906&ContentID=Content&UserID=&menup=0&_cb=&_cbdata=&_cbExec=1&_cbDispType=1&__pageState=0&__globalUrlParam=%7B%22PageID%22%3A%2246803%22%2C%22pageid%22%3A%2246803%22%7D&g_randomid=randomid_1051095574548506702800710985&np=%5B%2246803%40Content%40TwebCom_div_1_0%40220907102451613%22%5D&modename=amljaGFfZGFpbHlfY2hhcnRfN0Q5MTQ5NDE%3D&creator=cjzq"
    else:
        raise ValueError("type must be one of 'IF', 'IC', 'IM', 'IH'")
    decoded_data = urllib.parse.unquote(data)
    # 解析为字典格式
    parsed_params = urllib.parse.parse_qs(decoded_data)
    parsed_params["g_randomid"] = "randomid_" + str(uuid.uuid4().int)[:-11]
    updated_data = urllib.parse.urlencode(parsed_params, doseq=True)
    response = requests.post(
        "https://web.tinysoft.com.cn/website/loadContentDataAjax.tsl?ref=js",
        updated_data,
    )

    data = response.content.decode("utf-8", "ignore")
    data = json.loads(data)
    soup = BeautifulSoup(data["content"][0]["html"], "html.parser")
    script_content = soup.find("script").string
    match = re.search(r"var\s+SrcData\s*=\s*(\[.*?\]);", script_content, re.DOTALL)
    src_data_raw = match.group(1)
    # 将转义字符转换为实际字符
    src_data = json.loads(src_data_raw.encode().decode("unicode_escape"))
    data_df = pd.DataFrame(src_data)[
        [
            "日期",
            "主力合约",
            "期货价格",
            "现货价格",
            "基差",
            "到期日",
            "剩余天数",
            "期内分红",
            "矫正基差",
            "主力年化基差(%)",
            "年化基差(%)",
        ]
    ]

    return data_df


def generate_trading_date(
    begin_date: np.datetime64 = np.datetime64("2015-01-04"),
    end_date: np.datetime64 = np.datetime64("today"),
) -> Tuple[np.ndarray[np.datetime64]]:
    assert begin_date >= np.datetime64(
        "2015-01-04"
    ), "系统预设起始日期仅支持2015年1月4日以后"
    with open(
        Path(__file__).resolve().parent.joinpath("Chinese_special_holiday.txt"), "r"
    ) as f:
        chinese_special_holiday = pd.Series(
            [date.strip() for date in f.readlines()]
        ).values.astype("datetime64[D]")
    working_date = pd.date_range(begin_date, end_date, freq="B").values.astype(
        "datetime64[D]"
    )
    trading_date = np.setdiff1d(working_date, chinese_special_holiday)
    trading_date_df = pd.DataFrame(working_date, columns=["working_date"])
    trading_date_df["is_friday"] = trading_date_df["working_date"].apply(
        lambda x: x.weekday() == 4
    )
    trading_date_df["trading_date"] = (
        trading_date_df["working_date"]
        .apply(lambda x: x if x in trading_date else np.nan)
        .ffill()
    )
    return (
        trading_date,
        np.unique(
            trading_date_df[trading_date_df["is_friday"]]["trading_date"].values[1:]
        ).astype("datetime64[D]"),
    )


def load_holidays(filepath: str) -> list[str]:
    """
    一次性从文件中加载并清理节假日数据。
    """
    with open(filepath, "r", encoding="utf-8") as f:
        holidays = [
            line.strip() for line in f if line.strip() and not line.startswith("#")
        ]
    return holidays


def is_trading(date, holidays):
    """检查给定日期是否为交易日"""
    is_trading = np.is_busday(date, holidays=holidays)
    return is_trading


def get_latest_dates(engine, table_name: str, group_by_field: str = "code"):
    """
    从数据库获取每个分组字段的最新日期。
    :param engine: 数据库引擎
    :param table_name: 数据表名
    :param group_by_field: 分组字段，默认为 'code'
    :return: 包含最新日期的 DataFrame
    """
    query = text(
        f"SELECT `{group_by_field}`, MAX(`date`) as `latest_date` FROM `{table_name}` GROUP BY `{group_by_field}`"
    )
    try:
        latest_dates_df = pd.read_sql_query(query, engine)
        latest_dates_df["latest_date"] = pd.to_datetime(
            latest_dates_df["latest_date"]
        )  # 确保日期列是datetime类型
        print(f"成功从数据库中读取每个 {group_by_field} 的最新日期：")
        print(latest_dates_df)
    except Exception as e:
        print(f"读取数据库时发生错误: {e}")
        print("可能是第一次运行或表不存在。将创建一个空的DataFrame继续。")
        latest_dates_df = pd.DataFrame(columns=[group_by_field, "latest_date"])
    return latest_dates_df


def update_latest_dates(engine, latest_dates_df, info_name):
    """
    更新指定表中的最新日期。
    """
    if latest_dates_df is None or latest_dates_df.empty:
        print("没有数据提供. Skipping.")
        return
    try:
        with engine.connect() as connection:
            with connection.begin() as transaction:
                print(f"--- Starting update for '{info_name}' table ---")
                latest_dates_df["latest_date"] = pd.to_datetime(
                    latest_dates_df["latest_date"]
                ).dt.date
                for index, row in latest_dates_df.iterrows():
                    code_to_update = row["code"]
                    new_date = row["latest_date"]
                    update_query = text(
                        f"UPDATE `{info_name}` SET `updated_date` = :new_date WHERE `code` = :code_val"
                    )
                    connection.execute(
                        update_query, {"new_date": new_date, "code_val": code_to_update}
                    )
                print(f"成功更新 {len(latest_dates_df)} 条记录.")
    except Exception as e:
        print(f"An error occurred during the update: {e}")


def get_source_info(engine, info_name, additional_columns: list[str] = None):
    """
    读取数据获取的参数信息。
    """
    if additional_columns is None:
        additional_columns = []
    if len(additional_columns) == 0:
        info_query = text(f"SELECT code, updated_date FROM {info_name}")
    else:
        info_query = text(
            f"SELECT code, updated_date, {','.join(additional_columns)} FROM {info_name}"
        )
    info_df = pd.read_sql_query(info_query, engine)
    return info_df


def fetch_akshare_data(
    symbols_ak,
    latest_dates_dict,
    today_str,
    data_type: Literal["stock", "index"] = "stock",
):
    assert data_type in [
        "stock",
        "index",
    ], "data_type must be either 'stock' or 'index'"

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
                check_date = (latest_date - timedelta(days=3)).strftime(
                    "%Y%m%d"
                )  # akshare如果start或者end为周末，会有数据填充，如果周末包含在区间内则会自动删除
            else:
                check_date = latest_date.strftime("%Y%m%d")
            if data_type == "index":
                daily_df = ak.index_zh_a_hist(
                    symbol=code_ak,
                    start_date=check_date,
                    end_date=today_str,
                )
                # 数据清洗和处理
                data = daily_df[
                    ["日期", "开盘", "最高", "最低", "收盘", "成交量", "成交额"]
                ].copy()  # 使用 .copy() 避免 SettingWithCopyWarning
                data.rename(
                    columns={
                        "日期": "date",
                        "开盘": "OPEN",
                        "最高": "HIGH",
                        "最低": "LOW",
                        "收盘": "CLOSE",
                        "成交量": "VOLUME",
                        "成交额": "AMT",
                    },
                    inplace=True,
                )
            elif data_type == "stock":
                daily_df = ak.stock_zh_a_daily(
                    symbol=code_ak, start_date=check_date, end_date=today_str
                )
                # 数据清洗和处理
                data = daily_df[
                    ["date", "open", "high", "low", "close", "volume", "amount"]
                ].copy()  # 使用 .copy() 避免 SettingWithCopyWarning
                data.rename(
                    columns={
                        "open": "OPEN",
                        "high": "HIGH",
                        "low": "LOW",
                        "close": "CLOSE",
                        "volume": "VOLUME",
                        "amount": "AMT",
                    },
                    inplace=True,
                )

            if daily_df.empty:
                print("在指定日期范围内未获取到新数据。")
                continue
            print(f"成功获取 {len(data)} 条数据，额外获取了用于计算涨跌幅的数据")
            data["date"] = pd.to_datetime(data["date"])
            data["PCT_CHG"] = data["CLOSE"].pct_change() * 100
            data["code"] = code_db  # 插入用于识别代码的列
            # 确保使用datetime对象进行比较，以保证准确性
            data = data[data["date"] >= pd.to_datetime(start_date)]
            print(f"处理后剩余 {len(data)} 条新数据。")

            data_list.append(data)

        except Exception as e:
            print(f"通过 akshare 获取代码 {code_ak} 数据时出错: {e}")
    return data_list


def fetch_akshare_minbar_data(
    symbols_ak,
    latest_dates_dict,
    today_str,
    data_type: Literal["stock", "index"] = "index",
):
    # TODO: 目前只写了指数(含ETF)的分钟线，股票的分钟线后续再加
    assert data_type in [
        "stock",
        "index",
    ], "data_type must be either 'stock' or 'index'"

    """处理并从akshare获取指数数据"""
    print("\n--- 开始处理 akshare 指数/ETF数据 ---")
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
                check_date = (latest_date - timedelta(days=3)).strftime(
                    "%Y%m%d"
                )  # akshare如果start或者end为周末，会有数据填充，如果周末包含在区间内则会自动删除
            else:
                check_date = latest_date.strftime("%Y%m%d")
            if data_type == "index":
                minbar_df = ak.index_zh_a_hist_min_em(
                    symbol=code_ak,
                    start_date=check_date,
                    end_date=today_str,
                )
                # 数据清洗和处理
                data = minbar_df[
                    ["时间", "开盘", "最高", "最低", "收盘", "成交量", "成交额", "均价"]
                ].copy()  # 使用 .copy() 避免 SettingWithCopyWarning
                data.rename(
                    # TODO:这里应该写成time, 但是后续很多函数都是用的date，以后系统性改成time
                    columns={
                        "时间": "date",
                        "开盘": "OPEN",
                        "最高": "HIGH",
                        "最低": "LOW",
                        "收盘": "CLOSE",
                        "成交量": "VOLUME",
                        "成交额": "AMT",
                        "均价": "AVG_PRICE",
                    },
                    inplace=True,
                )
            elif data_type == "stock":
                print("股票的分钟线后续再加")
                continue

            if minbar_df.empty:
                print("在指定日期范围内未获取到新数据。")
                continue
            print(f"成功获取 {len(data)} 条数据，额外获取了用于计算涨跌幅的数据")
            data["date"] = pd.to_datetime(data["date"])
            data["PCT_CHG"] = data["CLOSE"].pct_change() * 100
            data["code"] = code_db  # 插入用于识别代码的列
            # 确保使用datetime对象进行比较，以保证准确性
            data = data[data["date"] >= pd.to_datetime(start_date)]
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
            data = data[
                [
                    "tradeDate",
                    "open",
                    "hight",
                    "low",
                    "close",
                    "pctChange",
                    "volume",
                    "amount",
                ]
            ]
            data = data.rename(
                columns={
                    "tradeDate": "date",
                    "open": "OPEN",
                    "hight": "HIGH",
                    "low": "LOW",
                    "close": "CLOSE",
                    "pctChange": "PCT_CHG",
                    "volume": "VOLUME",
                    "amount": "AMT",
                }
            )
            data["date"] = pd.to_datetime(data["date"], format="%Y%m%d")

            new_data = data[
                data["date"] >= pd.to_datetime(start_date)
            ].copy()  # 使用.copy()避免警告
            new_data["code"] = index_code  # 插入用于识别代码的列
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

            data = pd.DataFrame(data_json["data"])[
                [
                    "tradeDate",
                    "open",
                    "high",
                    "low",
                    "close",
                    "tradingVol",
                    "tradingValue",
                    "changePct",
                ]
            ]
            data = data.rename(
                columns={
                    "tradeDate": "date",
                    "open": "OPEN",
                    "high": "HIGH",
                    "low": "LOW",
                    "close": "CLOSE",
                    "tradingVol": "VOLUME",
                    "tradingValue": "AMT",
                    "changePct": "PCT_CHG",
                }
            )
            data["VOLUME"] *= 1e6
            data["AMT"] *= 1e8
            data["code"] = code  # 插入用于识别代码的列
            data["date"] = pd.to_datetime(data["date"])
            print(f"成功获取 {len(data)} 条新数据。")
            data_list.append(data)
        except Exception as e:
            print(f"处理中证代码 {code} 时出错: {e}")
    return data_list


def fetch_cni_data(symbols_cni, latest_dates_dict, today_str):
    """处理并从国证获取指数数据"""
    print("\n--- 开始处理 国证 指数数据 ---")
    data_list = []
    for code, code_cni in symbols_cni.items():
        print(f"\n>>> 正在处理代码: {code}")
        latest_date = latest_dates_dict.get(code)
        if not latest_date:
            print(f"警告: 在数据库中未找到代码 {code} 的最新日期，跳过。")
            continue

        start_date = (latest_date + timedelta(days=1)).strftime("%Y%m%d")
        check_date = (latest_date + timedelta(days=1)).strftime("%Y-%m-%d")
        today_date = datetime.now().strftime("%Y-%m-%d")
        if start_date > today_str:
            print("数据已是最新，无需更新。")
            continue
        print(f"数据库中最新日期为: {latest_date.date()}, 将从 {start_date} 开始获取。")

        try:
            url = f"https://hq.cnindex.com.cn/market/market/getIndexDailyDataWithDataFormat?indexCode={code_cni}&startDate={check_date}&endDate={today_date}&frequency=day"
            res = requests.get(url)
            data_json = res.json()["data"]
            if not data_json:
                print("国证 API 未返回有效数据。")
                continue

            data = pd.DataFrame(data_json["data"], columns=data_json["item"])[
                [
                    "timestamp",
                    "high",
                    "open",
                    "low",
                    "close",
                    "percent",
                    "amount",
                    "volume",
                ]
            ]
            data = data.rename(
                columns={
                    "timestamp": "date",
                    "open": "OPEN",
                    "high": "HIGH",
                    "low": "LOW",
                    "close": "CLOSE",
                    "volume": "VOLUME",
                    "amount": "AMT",
                    "percent": "PCT_CHG",
                }
            )
            data["code"] = code  # 插入用于识别代码的列
            data["date"] = pd.to_datetime(data["date"])
            print(f"成功获取 {len(data)} 条新数据。")
            data_list.append(data)
        except Exception as e:
            print(f"处理国证代码 {code} 时出错: {e}")
    return data_list


def save_data_to_database(
    all_new_data: list[pd.DataFrame], table_name, engine, holidays
):
    """合并数据，过滤并写入数据库"""
    print("\n--- 写入数据库 ---")

    if all_new_data:
        final_df = pd.concat(all_new_data, ignore_index=True)
        final_df["date"] = pd.to_datetime(
            final_df["date"]
        ).dt.date  # 确保date列是日期类型
        mask = final_df["date"].apply(lambda d: is_trading(d, holidays))
        final_df = final_df[mask]
        print(f"过滤后，剩余 {len(final_df)} 条交易日数据。")

        print(f"总计 {len(final_df)} 条新数据将被写入数据库。")

        try:
            final_df.to_sql(
                name=table_name,
                con=engine,
                if_exists="append",
                index=False,
                dtype={"date": sqlalchemy.types.Date},  # 明确指定date列的类型
            )
            print("\n数据成功写入数据库！")
        except Exception as e:
            print(f"\n数据写入数据库时发生错误: {e}")
    else:
        print("\n任务完成，没有新数据需要写入数据库。")
