import pandas as pd
import numpy as np
import mplfinance as mpf
import time
import matplotlib.pyplot as plt
from fetch_em_minbar import get_minutely_data, data_to_data_frame
from loguru import logger


def fetch_minbar_df(engine, date, code):
    df = pd.read_sql_query(
        f"select * from UpdatedData.stock_basic_data_ak_minbar where Date(`datetime`)='{date}' and code='{code}';",
        engine,
    )
    df.rename(
        columns={
            "OPEN": "Open",
            "HIGH": "High",
            "LOW": "Low",
            "CLOSE": "Close",
            "VOLUME": "Volume",
        },
        inplace=True,
    )
    df.set_index("datetime", inplace=True)
    return df


def calc_indicators(minbar_df):
    minbar_df["PRICE_DEV"] = (
        (minbar_df["Close"] - minbar_df["AVG_PRICE"]) / minbar_df["AVG_PRICE"] * 100
    )
    short_ema = minbar_df["Close"].ewm(span=12, adjust=False).mean()
    long_ema = minbar_df["Close"].ewm(span=26, adjust=False).mean()
    minbar_df["long_ema"] = long_ema
    minbar_df["short_ema"] = short_ema

    macd = short_ema - long_ema
    signal = macd.ewm(span=9, adjust=False).mean()
    hist = macd - signal
    minbar_df["MACD"] = macd
    minbar_df["MACD_signal"] = signal
    minbar_df["MACD_hist"] = hist

    low_list = minbar_df["Low"].rolling(window=9, min_periods=1).min()
    high_list = minbar_df["High"].rolling(window=9, min_periods=1).max()
    rsv = (minbar_df["Close"] - low_list) / (high_list - low_list) * 100

    kdj_k = rsv.ewm(com=2).mean()
    kdj_d = kdj_k.ewm(com=2).mean()
    kdj_j = 3 * kdj_k - 2 * kdj_d

    minbar_df["KDJ_K"] = kdj_k
    minbar_df["KDJ_D"] = kdj_d
    minbar_df["KDJ_J"] = kdj_j


def find_signals(minbar_df):
    buy_signals = []
    sell_signals = []
    # for i in range(len(minbar_df)-15, len(minbar_df)):
    for i in range(5, len(minbar_df)):
        if (
            # minbar_df["PRICE_DEV"].iloc[i]
            # < minbar_df["PRICE_DEV"]
            # .iloc[:i]
            # .rolling(window=30, min_periods=10)
            # .median()
            # .iloc[-1]
            minbar_df["MACD_hist"].iloc[i - 1]
            < minbar_df["MACD_hist"].iloc[: i - 1].quantile(0.20)
            and minbar_df["MACD_hist"].iloc[i - 1] < minbar_df["MACD_hist"].iloc[i - 2]
            and minbar_df["MACD_hist"].iloc[i] > minbar_df["MACD_hist"].iloc[i - 1]
            and minbar_df["KDJ_K"].iloc[i] < 20
        ):
            buy_signals.append(minbar_df.index[i])

        if (
            # minbar_df["PRICE_DEV"].iloc[i]
            # > minbar_df["PRICE_DEV"]
            # .iloc[:i]
            # .rolling(window=30, min_periods=10)
            # .median()
            # .iloc[-1]
            minbar_df["MACD_hist"].iloc[i - 1]
            > minbar_df["MACD_hist"].iloc[: i - 1].quantile(0.80)
            and minbar_df["MACD_hist"].iloc[i - 1] > minbar_df["MACD_hist"].iloc[i - 2]
            and minbar_df["MACD_hist"].iloc[i] < minbar_df["MACD_hist"].iloc[i - 1]
            and minbar_df["KDJ_K"].iloc[i] > 80
        ):
            sell_signals.append(minbar_df.index[i])
    return buy_signals, sell_signals


def make_apds(minbar_df, buy_signals, sell_signals):
    buy_marker = np.full(len(minbar_df), np.nan)
    sell_marker = np.full(len(minbar_df), np.nan)
    buy_idx = minbar_df.index.get_indexer(buy_signals)
    sell_idx = minbar_df.index.get_indexer(sell_signals)
    buy_marker[buy_idx] = minbar_df["Close"].iloc[buy_idx]
    sell_marker[sell_idx] = minbar_df["Close"].iloc[sell_idx]
    apds = []
    if len(buy_signals) > 0:
        apds.append(
            mpf.make_addplot(
                buy_marker, type="scatter", markersize=100, marker="^", color="red"
            )
        )
    if len(sell_signals) > 0:
        apds.append(
            mpf.make_addplot(
                sell_marker, type="scatter", markersize=100, marker="v", color="green"
            )
        )
    return apds


def plot_multiple_dates(code, minbar_df):
    calc_indicators(minbar_df)
    print("---{}---".format(code))
    buy_signals, sell_signals = find_signals(minbar_df)
    print(f"Buy signals: {buy_signals}")
    print(f"Sell signals: {sell_signals}")
    # apds = make_apds(minbar_df, buy_signals, sell_signals)
    # addplots = [
    #     mpf.make_addplot(minbar_df["AVG_PRICE"], panel=0, color="orange", width=1.5),
    #     mpf.make_addplot(minbar_df["short_ema"], panel=0, color="blue", width=1.5),
    #     mpf.make_addplot(minbar_df["long_ema"], panel=0, color="purple", width=1.5),
    #     mpf.make_addplot(minbar_df["MACD"], panel=1, color="b", ylabel="MACD"),
    #     mpf.make_addplot(minbar_df["MACD_signal"], panel=1, color="r"),
    #     mpf.make_addplot(minbar_df["MACD_hist"], panel=1, color="g", type="bar"),
    #     mpf.make_addplot(minbar_df["KDJ_K"], panel=2, color="m", ylabel="KDJ"),
    #     mpf.make_addplot(minbar_df["KDJ_D"], panel=2, color="c"),
    #     mpf.make_addplot(minbar_df["KDJ_J"], panel=2, color="y"),
    #     mpf.make_addplot(
    #         minbar_df["PRICE_DEV"], panel=3, color="gray", ylabel="Price Dev (%)"
    #     ),
    #     *apds,
    # ]
    # mpf.plot(
    #     minbar_df,
    #     type="candle",
    #     title=f"{code} 1-Minute K-Line",
    #     ylabel="Price",
    #     show_nontrading=False,
    #     addplot=addplots,
    # )


if __name__ == "__main__":
    while True:
        for code, name, market in [
            # ("002460", "赣", 0),
            # ("159755", "电池", 0),
            ("588200", "芯片", 1),
            ("513050", "中概", 1),
            ("513090", "证券", 1),
        ]:
            data_test = get_minutely_data(market, code)
            df_data_test, last_trend = data_to_data_frame(data_test)
            tmp = last_trend.split(",")
            logger.info(f"Code: {code}, Trend: {tmp[0]} -- {tmp[4]} -- {tmp[-1]}")
            plot_multiple_dates(f"{name}", df_data_test)
