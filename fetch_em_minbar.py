from io import StringIO
import json
import pandas as pd
import requests
from loguru import logger
import time


def _handle_event(event_data) -> str:
    """
    解析event数据
    :param event_data: SSE数据
    :return: 事件的数据字段
    """
    lines = event_data.strip().split("\n")
    data = ""

    for line in lines:
        if line.startswith("event:"):  # 东财分时数据的事件无event
            event_type = line.replace("event:", "").strip()
        elif line.startswith("data:"):
            data = line.replace("data:", "").strip()
    return data


def get_minutely_data(market: int, code: str) -> dict:
    """
    获取最新的分时数据
    :param code: 股票代码，6位数字格式，比如：“000001”。
    :return: 数据字典
    """
    # url格式，需要调用者依次填充：市场代码（0：深圳，1：上海），股票代码，日期窗口
    url_format = (
        "https://45.push2.eastmoney.com/api/qt/stock/trends2/sse?fields1=f1,f2,f3,f4,f5,f6,f7,f8,"
        "f9,f10,f11,f12,f13,f14,f17&fields2=f51,f52,f53,f54,f55,f56,f57,"
        "f58&mpi=1000&ut=fa5fd1943c7b386f172d6893dbfba10b&secid={market}.{code}"
        "&ndays={days}&iscr=0&iscca=0&wbp2u=1849325530509956|0|1|0|web"
    )

    url = url_format.format(market=market, code=code, days=1)  # 请求url
    headers = {"Accept": "text/event-stream"}

    response = requests.get(url, headers=headers, stream=True)  # 请求数据，开启流式传输

    if response.status_code == 200:
        event_data = ""
        for chunk in response.iter_content(chunk_size=None):  # 不断地获取数据
            data_decoded = chunk.decode("utf-8")  # 将字节流解码成字符串
            event_data += data_decoded
            parts = event_data.split("\n\n")
            if len(parts) > 1:  # 获取到一条完整的事件后，对数据进行解析。
                data = _handle_event(parts[0])
                return json.loads(data)


def data_to_data_frame(data: dict) -> pd.DataFrame:
    try:
        trends = data["data"]["trends"]
        trends_str = json.dumps(trends)
        trend_csv_content = "Time,Open,Close,High,Low,Volume,AMT,AVG_PRICE\n"
        trend_csv_content += trends_str.replace('", "', "\n").strip('"[]')

        type_mapping = {
            "Open": float,
            "High": float,
            "Low": float,
            "Close": float,
            "Volume": float,
            "AMT": float,
            "AVG_PRICE": float,
        }
        df_data = pd.read_csv(
            StringIO(trend_csv_content),
            delimiter=",",
            dtype=type_mapping,
            parse_dates=["Time"],
            index_col="Time",
        )
        return df_data, trends[-1]
    except Exception as e:
        logger.error(f"异常：{e}")
        return None


if __name__ == "__main__":  # 循环获取数据
    intervals = []
    last_time = None
    for i in range(50):
        start_time = time.time()
        data_test = get_minutely_data("513090")
        df_data_test, last_trend = data_to_data_frame(data_test)
        end_time = time.time()
        if last_time is not None:
            intervals.append(start_time - last_time)
        last_time = start_time
    if intervals:
        avg_interval = sum(intervals) / len(intervals)
        logger.info(f"平均间隔: {avg_interval:.3f} 秒")
    # while True:
    #     data_test = get_minutely_data("NVDA")
    #     df_data_test, last_trend = data_to_data_frame(data_test)
    #     logger.info(last_trend)
