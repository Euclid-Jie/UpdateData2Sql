import sqlalchemy
import pandas as pd
from utils import update_loc_method
from FOF99Api import FOF99Api
from config import SQL_PASSWORDS, SQL_HOST

engine = sqlalchemy.create_engine(
    f"mysql+pymysql://dev:{SQL_PASSWORDS}@{SQL_HOST}:3306/Nav?charset=utf8"
)

# 读取所有数据
data = pd.read_sql_query("SELECT * FROM Nav.跟踪产品池", engine)
fof_99 = FOF99Api()

for i, row in data.iterrows():

    if pd.notna(row["管理人登记编号"]):
        continue
    print(f"正在更新第{i + 1}条数据: {row['基金名称']}")
    registerNo = row["备案编码"]
    fund_info = fof_99.get_fund_info(registerNo)
    for data_name, var in {
        "advisor": "管理人",
        "inception_date": "成立日期",
        "puton_date": "备案日期",
    }.items():
        update_loc_method(
            engine=engine,
            table_name="跟踪产品池",
            key="备案编码",
            var=var,
            data={row["备案编码"]: fund_info[data_name]},
        )
    company_info = fund_info["FundsBase"]
    for data_name, var in {
        "scale": "管理人规模",
        "register_code": "管理人登记编号",
    }.items():
        update_loc_method(
            engine=engine,
            table_name="跟踪产品池",
            key="备案编码",
            var=var,
            data={row["备案编码"]: company_info[data_name]},
        )
    
    
