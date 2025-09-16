import akshare as ak
import pandas as pd
from utils import connect_to_database
from sqlalchemy import  text
from datetime import datetime
import logging

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

def main(engine):
    logging.info("成分股数据更新开始...")

    # Define the indices to process
    symbols = ["000300", "000985", "000852", "000905"]

    for symbol in symbols:
        table_name = f"index_{symbol}_cons"
        logging.info(f"正在处理 index: {symbol} ， 表名: {table_name}")

        # 1. Fetch new data from akshare
        try:
            new_data_df = ak.index_stock_cons_weight_csindex(symbol=symbol)
            if new_data_df.empty:
                logging.warning(f"未返回数据的指数 {symbol} ，跳过处理。")
                continue
        except Exception as e:
            logging.error(f"获取指数 {symbol} 数据失败: {e}")
            continue  # Move to the next symbol

        # 2. Standardize the DataFrame
        new_data_df = new_data_df.rename(
            columns={
                "日期": "trade_date",
                "指数代码": "index_code",
                "成分券代码": "con_code",
                "权重": "weight",
            }
        )
        new_data_df = new_data_df[["index_code", "con_code", "trade_date", "weight"]]
        # Ensure the date format is consistent before checking the database
        new_data_df["trade_date"] = pd.to_datetime(new_data_df["trade_date"]).dt.date

        # Get the trade date from the new data. This is the source of truth.
        latest_trade_date = new_data_df["trade_date"].iloc[0]

        # 3. Check if this date's data already exists in the database
        data_exists = False
        try:
            with engine.connect() as connection:
                # Use sqlalchemy.text() for safe query parameterization
                query = text(
                    f"SELECT 1 FROM `{table_name}` WHERE trade_date = :date LIMIT 1"
                )
                result = connection.execute(query, {"date": latest_trade_date}).scalar()
                if result == 1:
                    data_exists = True
        except Exception as e:
            # This handles the case where the table doesn't exist yet
            if "no such table" in str(e) or "does not exist" in str(e):
                logging.info(
                    f"Table '{table_name}' 不存在，将创建新表并插入数据。"
                )
            else:
                logging.error(f" '{table_name}' 的数据库检查失败: {e}")
                continue

        # 4. If data doesn't exist for the date, append it
        if not data_exists:
            try:
                new_data_df.to_sql(
                    table_name,
                    engine,
                    if_exists="append",  # Appends new data; creates table if it doesn't exist
                    index=False,
                )
                logging.info(
                    f"成功添加 {len(new_data_df)} 条记录到 '{table_name}' 表，日期: {latest_trade_date}."
                )
            except Exception as e:
                logging.error(f"写入表 '{table_name}' 失败: {e}")
        else:
            logging.info(
                f"日期 {latest_trade_date} 的数据已存在于 '{table_name}' 表中，无需更新."
            )

    logging.info("所有指数数据更新任务已完成.")


if __name__ == "__main__":
    db_engine = connect_to_database()
    if db_engine:
        # Run the main update logic
        main(db_engine)
        # Dispose of the engine connection pool when the script is finished
        db_engine.dispose()
        logging.info("数据库连接已关闭.")