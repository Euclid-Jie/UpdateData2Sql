import akshare as ak
import pandas as pd
from utils import connect_to_database

# 更新原有数据库中的新数据，因为akshare这个接口只能返回当天的成分股，所以需要每天运行然后dropduplicates

# 创建数据库连接
engine = connect_to_database()

# 获取当前最新的沪深300成分股列表
symbols = ["000300", "000985", "000852", "000905"]
for symbol in symbols:
    print(f"正在处理指数: {symbol}")
    table_name = f"index_{symbol}_cons"

    # 获取新数据
    new_data_df = ak.index_stock_cons_weight_csindex(symbol=symbol)

    try:
        # 只查询已有的日期和指数代码组合
        existing_keys_df = pd.read_sql_query(
            f"SELECT DISTINCT 日期, 指数代码 FROM {table_name}",
            engine
        )

        if not existing_keys_df.empty:
            # 合并键列用于比较
            existing_keys_df['key'] = existing_keys_df['日期'].astype(str) + existing_keys_df['指数代码'].astype(str)
            new_data_df['key'] = new_data_df['日期'].astype(str) + new_data_df['指数代码'].astype(str)

            # 找出新数据中不存在的记录
            new_records_df = new_data_df[~new_data_df['key'].isin(existing_keys_df['key'])]
            new_records_df = new_records_df.drop(columns=['key'])

            # 插入新记录
            if not new_records_df.empty:
                new_records_df.to_sql(table_name, engine, if_exists='append', index=False)
                print(f"新增 {len(new_records_df)} 条记录到表 {table_name}")
            else:
                print(f"没有新记录需要插入表 {table_name}")
        else:
            # 表为空，直接插入所有数据
            new_data_df.to_sql(table_name, engine, if_exists='replace', index=False)
            print(f"初始化表 {table_name}，插入 {len(new_data_df)} 条记录")

    except Exception as e:
        # 表可能不存在，创建新表
        if "does not exist" in str(e) or "no such table" in str(e):
            new_data_df.to_sql(table_name, engine, if_exists='replace', index=False)
            print(f"创建新表 {table_name}，插入 {len(new_data_df)} 条记录")
        else:
            print(f"处理数据时出错: {e}")
engine.dispose()
