from utils import load_bais
import sqlalchemy
import os

SQL_PASSWORDS = os.environ["SQL_PASSWORDS"]
SQL_HOST = os.environ["SQL_HOST"]

def write_to_sql(data, table_name, engine):
    data.to_sql(
        name=table_name,
        con=engine,
        if_exists="replace",
        index=False,
        dtype={
            "日期": sqlalchemy.types.Date,
            "主力合约": sqlalchemy.types.String(20),
            "到期日": sqlalchemy.types.Date,
            "剩余天数": sqlalchemy.types.Integer,
        },
    )


if __name__ == "__main__":
    engine = sqlalchemy.create_engine(
        f"mysql+pymysql://dev:{SQL_PASSWORDS}@{SQL_HOST}:3306/UpdatedData?charset=utf8"
    )
    print("Updating IF/IC/IM data...")
    for future_type in ["IF", "IC", "IM", "IH"]:
        data = load_bais(future_type)
        write_to_sql(data, f"{future_type}_data", engine)
        print(f"{future_type} data updated successfully.")
