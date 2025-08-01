import pandas as pd
import numpy as np
from WindPy import w
from typing import Literal
from pathlib import Path

# modify date: 2025-8-1
# modify by: Euclid-Jie
# description: 删掉了F-String的使用

class WindWareHouse:
    def __init__(self) -> None:
        """
        Initialize the WindWareHouse object.
        """
        w.start()

    @staticmethod
    def wind_datetime_covert(dt: np.datetime64, format: Literal["D", "dt"] = "dt"):
        """
        Convert numpy datetime64 to string format.

        Args:
            dt (np.datetime64): The datetime to be converted.
            format (Literal["D", "dt"], optional): The format of the converted datetime.
                "D" for date format, "dt" for datetime format. Defaults to "dt".

        Returns:
            str: The converted datetime string.
        """
        if format == "D":
            return np.datetime_as_string(dt, unit="D")
        elif format == "dt":
            return np.datetime_as_string(dt, unit="s").replace("T", " ")

    @staticmethod
    def add_exchange_prefix(stock_code):
        if stock_code.startswith("6"):
            return stock_code + ".SH"
        elif stock_code.startswith("0") or stock_code.startswith("3"):
            return stock_code + ".SZ"
        else:
            return stock_code

    def get_data(
        self,
        code: str = "510050.SH",
        fields: str = "open,close,high,low,volume",
        begin_date: np.datetime64 = np.datetime64("2020-06-06"),
        end_date: np.datetime64 = np.datetime64("today"),
        freq: Literal["D", "60M", "30M", "15M", "10M", "5M", "1M"] = "D",
    ):
        """
        Get ETF/Stock data.

        Args:
            code (str, optional): The code of the ETF/Stock. Defaults to "510050.SH".
            fields (str, optional): The fields of the data. Defaults to "open,close,high,low,volume".
            begin_date (np.datetime64, optional): The start date of the data. Defaults to np.datetime64("2020-06-06").
            end_date (np.datetime64, optional): The end date of the data. Defaults to np.datetime64("today").
            freq (Literal["D", "60M", "30M", "15M", "10M", "5M", "1M"], optional): The frequency of the data.
                "D" for daily, "60M" for hourly, "30M" for every 30 minutes, "15M" for every 15 minutes,
                "10M" for every 10 minutes, "5M" for every 5 minutes, "1M" for every 1 minute.
                Defaults to "D".

        Returns:
            pd.DataFrame: The ETF/Stock data.
        """
        self.code = code
        if freq == "D":
            data = self.get_data_daily(self.code, begin_date, end_date, fields)
            data.index.name = "date"
        if "M" in freq:
            data = self.get_data_intraday(
                self.code, begin_date, end_date, freq=freq, fields=fields
            )
            data.index.name = "datetime"
        data["code"] = code
        return data.reset_index(drop=False)

    @staticmethod
    def get_data_daily(
        code: str = "510050.SH",
        begin_date: np.datetime64 = np.datetime64("2020-06-06"),
        end_date: np.datetime64 = np.datetime64("today"),
        fields: str = "open,close,high,low,volume",
    ):
        """
        Get daily ETF/Stock  data.

        Args:
            code (str, optional): The code of the ETF/Stock. Defaults to "510050.SH".
            begin_date (np.datetime64, optional): The start date of the data. Defaults to np.datetime64("2020-06-06").
            end_date (np.datetime64, optional): The end date of the data. Defaults to np.datetime64("today").

        Returns:
            pd.DataFrame: The daily ETF/Stock data.
        """
        _, data = w.wsd(
            code,
            fields,
            WindWareHouse.wind_datetime_covert(begin_date, "D"),
            WindWareHouse.wind_datetime_covert(end_date, "D"),
            PriceAdj="F",
            usedf=True,
        )
        if len(data) == 1 and begin_date == end_date:
            data.index = [np.datetime_as_string(begin_date, unit="D")]
        return data

    @staticmethod
    def get_data_intraday(
        code: str = "510050.SH",
        begin_date: np.datetime64 = np.datetime64("2024-06-06 10:00"),
        end_date: np.datetime64 = np.datetime64("today"),
        freq: Literal["60M", "30M", "15M", "10M", "5M", "1M"] = "5M",
        fields: str = "open,close,high,low,volume",
    ):
        """
        Get intraday ETF/Stock data.

        Args:
            code (str, optional): The code of the ETF/Stock. Defaults to "510050.SH".
            begin_date (np.datetime64, optional): The start date of the data. Defaults to np.datetime64("2024-06-06 10:00").
            end_date (np.datetime64, optional): The end date of the data. Defaults to np.datetime64("today").
            freq (Literal["60M", "30M", "15M", "10M", "5M", "1M"], optional): The frequency of the data.
                "60M" for hourly, "30M" for every 30 minutes, "15M" for every 15 minutes,
                "10M" for every 10 minutes, "5M" for every 5 minutes, "1M" for every 1 minute.
                Defaults to "5M".

        Returns:
            pd.DataFrame: The intraday ETF/Stock data.
        """
        if end_date.dtype == "M8[D]":
            end_date = end_date + np.timedelta64(15, "h")
        _, data = w.wsi(
            code,
            fields,
            WindWareHouse.wind_datetime_covert(begin_date, "dt"),
            WindWareHouse.wind_datetime_covert(end_date, "dt"),
            PriceAdj="F",
            options=f"BarSize={int(freq[:-1])}",
            usedf=True,
        )
        return data

    def get_option_code(
        self,
        date: np.datetime64 = np.datetime64("today"),
        us_code: str = "510050.SH",
        call_put: Literal["all", "call", "put"] = "all",
    ):
        """
        Get option code.

        Args:
            date (np.datetime64, optional): The date of the option code. Defaults to np.datetime64("today").
            us_code (str, optional): The code of the underlying stock. Defaults to "510050.SH".
            call_put (Literal["all", "call", "put"], optional): The type of the option. Defaults to "all".

        Returns:
            pd.DataFrame: The option code.
        """
        _, options_code = w.wset(
            "optionchain",
            "date={};us_code={};call_put={}".format(
                self.wind_datetime_covert(date, format="D"),
                us_code,
                call_put,
            ),
            usedf=True,
        )
        return options_code

    @staticmethod
    def get_option_info(options_code):
        """
        Get option info.

        Args:
            options_code (pd.DataFrame): The option code.

        Returns:
            pd.DataFrame: The option info.
        """
        _, info = w.wss(
            options_code,
            "options_tradecode,underlyingwindcode,startdate,lasttradingdate,ptmtradeday,ptmday,exe_ratio,gamma,delta,vega,theta,rho",
            usedf=True,
        )
        return info

    @staticmethod
    def get_bench_cons(bench_symbol: str = Literal["000300.SH"]) -> list[str]:
        _, cons = w.wset(
            "sectorconstituent",
            "date={};windcode={}".format(
                WindWareHouse.wind_datetime_covert(np.datetime64("today"), "D"),
                bench_symbol,
            ),
            usedf=True,
        )
        return cons


if __name__ == "__main__":
    demo = WindWareHouse()
    # data = demo.get_data(
    #     code="512000.SH",
    #     fields="open,close,high,low,volume",
    #     begin_date=np.datetime64("2024-01-02 09:30"),
    #     end_date=np.datetime64("2024-01-02"),
    #     freq="60M",
    # )
    data = demo.get_data(
        code="10008482.SH",
        fields="close,open,high,low,volume,amt,chg,pct_chg,oi",
        begin_date=np.datetime64("2023-01-02"),
        end_date=np.datetime64("2024-01-02"),
        freq="1M",
    )
    save_foler = Path("data")
    save_foler.mkdir(parents=True, exist_ok=True)
    data.to_csv(
        save_foler.joinpath("{}.csv".format(data["code"].values[0])),
        index=False,
        encoding="utf-8-sig",
    )
