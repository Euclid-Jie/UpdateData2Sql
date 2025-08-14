from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
from pathlib import Path
import requests
from typing import Literal, Tuple
import re
import urllib.parse
import json
import uuid
import time
import sqlalchemy


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
