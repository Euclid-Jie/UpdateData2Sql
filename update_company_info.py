import sqlalchemy
from utils import get_company_base_info, update_loc_method
from FOF99Api import FOF99Api

SQL_PASSWORDS = ""
SQL_HOST = ""
FOF_99_TOEKN = ""

engine = sqlalchemy.create_engine(
    f"mysql+pymysql://dev:{SQL_PASSWORDS}@{SQL_HOST}:3306/Euclid?charset=utf8"
)
import pandas as pd

# 读取所有数据
data = pd.read_sql_query("SELECT * FROM Euclid.量化私募管理人列表", engine)
fof_99 = FOF99Api()
fof_99.token = FOF_99_TOEKN

for i, row in data.iterrows():
    if pd.notna(row["管理人名称"]):
        continue
    print(f"正在更新第{i + 1}条数据: {row['协会名称']}")
    info = get_company_base_info(row["协会名称"])
    for data_name, var in {
        "registerNo": "登记编号",
        "establishDate": "成立日期",
        "fundCount": "运作中产品数",
    }.items():
        update_loc_method(
            engine=engine,
            table_name="量化私募管理人列表",
            key="协会名称",
            var=var,
            data={row["协会名称"]: info[data_name].item()},
        )

    fof_99_info = fof_99.get_company_info_from_code(info["registerNo"].item())
    for data_name, var in {
        "company_name": "管理人名称",
        "strategy": "核心策略",
        "scale": "管理规模",
        "member_type": "会员类型",
    }.items():
        update_loc_method(
            engine=engine,
            table_name="量化私募管理人列表",
            key="协会名称",
            var=var,
            data={row["协会名称"]: fof_99_info[data_name]},
        )
