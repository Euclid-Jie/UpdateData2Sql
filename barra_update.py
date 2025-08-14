import sqlalchemy
import requests
from config import SQL_PASSWORDS, SQL_HOST

def connect_to_database():
    """创建并返回数据库引擎"""
    print("连接到数据库...")
    # 数据库连接
    engine = sqlalchemy.create_engine(
        f"mysql+pymysql://dev:{SQL_PASSWORDS}@{SQL_HOST}:3306/UpdatedData?charset=utf8"
    )
    return engine