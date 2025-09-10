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
    # 定义表名
    table_name = f"index_{symbol}_cons"

    # 获取新数据
    new_data_df = ak.index_stock_cons_weight_csindex(symbol=symbol)

    try:
        # 尝试读取现有数据
        existing_data_df = pd.read_sql_table(table_name, engine)

        combined_df = pd.concat([existing_data_df, new_data_df], ignore_index=True)
        combined_df = combined_df.drop_duplicates(
            subset=["日期", "指数代码"]
        ).reset_index(drop=True)

    except Exception as e:
        print(f"读取现有数据时出错: {e}, 将创建新表")
        combined_df = new_data_df

    # 写入数据库
    combined_df.to_sql(table_name, engine, if_exists="replace", index=False)
    print(f"数据已更新到表 {table_name}")
    print(f"新增 {len(new_data_df)} 条记录，当前总共 {len(combined_df)} 条记录")
engine.dispose()
