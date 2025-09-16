import akshare as ak
import pandas as pd
from utils import connect_to_database
from datetime import datetime

# 创建数据库连接
engine = connect_to_database()

# 获取当前日期
current_date = datetime.now().strftime("%Y%m%d")

# 定义要处理的指数
symbols = ["000300", "000985", "000852", "000905"]

for symbol in symbols:
    print(f"正在处理指数: {symbol}")
    table_name = f"index_{symbol}_cons"

    try:
        # 获取指数成分股权重数据
        new_data_df = ak.index_stock_cons_weight_csindex(symbol=symbol)

        # 重命名列以匹配数据库表结构
        new_data_df = new_data_df.rename(
            columns={
                "日期": "trade_date",
                "指数代码": "index_code",
                "成分券代码": "con_code",
                "权重": "weight",
            }
        )

        # 选择需要的列
        new_data_df = new_data_df[["index_code", "con_code", "trade_date", "weight"]]

        # 检查表是否已存在
        try:
            query_date = f"SELECT MAX(trade_date) FROM `{table_name}`"
            latest_date = pd.read_sql_query(query_date, engine).iloc[0, 0]
            query_data = f"SELECT * FROM `{table_name}` WHERE trade_date = {latest_date}"
            existing_data = pd.read_sql_query(query_data, engine)

            # 找出新数据中不存在的记录
            existing_keys = existing_data[["trade_date", "con_code"]].astype(str).apply(
                tuple, axis=1
            )
            new_keys = new_data_df[["trade_date", "con_code"]].astype(str).apply(tuple, axis=1)

            # 找出新数据中不存在的记录
            new_records_df = new_data_df[~new_keys.isin(existing_keys)]

            # 插入新记录
            if not new_records_df.empty:
                new_records_df['trade_date'] = pd.to_datetime(new_records_df['trade_date']).dt.date
                new_records_df.to_sql(
                    table_name, engine, if_exists="append", index=False
                )
                print(f"新增 {len(new_records_df)} 条记录到表 {table_name}")
                print(f"新增交易日: {new_records_df['trade_date'].unique()}")
            else:
                print(f"没有新记录需要插入表 {table_name}")

        except Exception as e:
            # 表不存在，创建新表并插入所有数据
            if "does not exist" in str(e) or "no such table" in str(e):
                new_data_df.to_sql(table_name, engine, if_exists="replace", index=False)
                print(f"创建新表 {table_name}，插入 {len(new_data_df)} 条记录")
            else:
                raise e

    except Exception as e:
        print(f"获取 {symbol} 数据时出错: {e}")
        continue

# 关闭连接
engine.dispose()
print("所有指数数据更新完成")
