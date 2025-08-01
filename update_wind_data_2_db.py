import numpy as np
import pandas as pd
import sqlalchemy
from WindWareHouse import WindWareHouse
from config import SQL_PASSWORDS, SQL_HOST

wind_warehouse = WindWareHouse()
engine = sqlalchemy.create_engine(
    f"mysql+pymysql://dev:{SQL_PASSWORDS}@{SQL_HOST}:3306/UpdatedData?charset=utf8"
)

bench_info_wind = pd.read_sql_query("SELECT * FROM bench_info_wind", engine)
local_now = np.datetime64("now") + np.timedelta64(8, "h")
# TODO 1.数据源使用公开的API 2.非交易日也无需更新
for i, v in bench_info_wind.iterrows():
    # 检查数据是否需要更新
    # 因为数据15:00更新, 如果当前时间小于15:00, 则不更新
    if np.datetime64(v["updated_date"]) < (local_now - np.timedelta64(15, "h")).astype(
        "datetime64[D]"
    ):
        data = wind_warehouse.get_data(
            code=v["code"],
            fields="open,high,low,close,pct_chg,volume,amt",
            begin_date=np.datetime64(v["updated_date"]) + np.timedelta64(1, "D"),
            freq="D",
        )
        data = data[data["AMT"].notna()]
        data.to_sql(
            name="bench_basic_data",
            con=engine.connect(),
            if_exists="append",
            index=False,
        )
        bench_info_wind.loc[i, "updated_date"] = data["date"].values[-1]
        print(
            "{} has been updated to {}".format(
                v["name"], bench_info_wind.loc[i, "updated_date"]
            )
        )
    else:
        print(
            "{} end date is {}, no need to update".format(
                v["name"], bench_info_wind.loc[i, "updated_date"]
            )
        )

    bench_info_wind.to_sql(
        name="bench_info_wind",
        con=engine.connect(),
        if_exists="replace",
        index=False,
    )
