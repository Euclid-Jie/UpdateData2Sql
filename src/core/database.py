"""
数据库核心模块
包含数据库连接和操作功能
"""

import sqlalchemy
import pandas as pd
from datetime import datetime
from typing import Dict, List, Optional
from config.database import get_database_url


def connect_to_database():
    """创建并返回数据库引擎"""
    print("连接到数据库...")
    # 数据库连接
    engine = sqlalchemy.create_engine(get_database_url())
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


def get_latest_dates(engine: sqlalchemy.engine.Engine, table_name: str) -> pd.DataFrame:
    """获取表中每个代码的最新日期"""
    query = f"""
    SELECT code, MAX(date) as latest_date
    FROM {table_name}
    GROUP BY code
    """
    return pd.read_sql(query, engine)


def update_latest_dates(
    engine: sqlalchemy.engine.Engine, 
    latest_dates_df: pd.DataFrame, 
    info_table_name: str
):
    """更新信息表中的最新日期"""
    with engine.connect() as conn:
        with conn.begin():
            for _, row in latest_dates_df.iterrows():
                sql_text = f"""
                UPDATE {info_table_name} 
                SET updated_date = '{row['latest_date']}' 
                WHERE code = '{row['code']}'
                """
                conn.execute(sqlalchemy.text(sql_text))


def get_source_info(
    engine: sqlalchemy.engine.Engine, 
    info_table_name: str, 
    additional_columns: Optional[List[str]] = None
) -> pd.DataFrame:
    """获取数据源信息"""
    columns = ["code", "updated_date"]
    if additional_columns:
        columns.extend(additional_columns)
    
    columns_str = ", ".join(columns)
    query = f"SELECT {columns_str} FROM {info_table_name}"
    return pd.read_sql(query, engine)


def save_data_to_database(
    data_list: List[pd.DataFrame], 
    table_name: str, 
    engine: sqlalchemy.engine.Engine, 
    holidays: List[str]
):
    """保存数据到数据库"""
    if not data_list:
        print("没有新数据需要保存")
        return
    
    # 合并所有数据
    combined_data = pd.concat(data_list, ignore_index=True)
    
    # 过滤掉节假日数据
    combined_data = combined_data[~combined_data['date'].isin(holidays)]
    
    if combined_data.empty:
        print("过滤节假日后没有数据需要保存")
        return
    
    # 保存到数据库
    try:
        combined_data.to_sql(
            table_name, 
            engine, 
            if_exists='append', 
            index=False,
            method='multi'
        )
        print(f"成功保存 {len(combined_data)} 条数据到表 {table_name}")
    except Exception as e:
        print(f"保存数据时出错: {e}")
        raise
