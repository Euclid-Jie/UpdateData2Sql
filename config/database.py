"""
数据库配置文件
"""

import os
from config.settings import get_env_config

# 从原config.py文件迁移的配置
SQL_PASSWORDS = "your_password_here"  # 请替换为实际密码
SQL_HOST = "localhost"

# 从环境变量获取数据库配置
def get_database_config():
    """获取数据库配置"""
    config = get_env_config()
    db_config = config["database"]
    
    # 从环境变量覆盖配置
    if os.getenv("SQL_PASSWORDS"):
        SQL_PASSWORDS = os.getenv("SQL_PASSWORDS")
    if os.getenv("SQL_HOST"):
        SQL_HOST = os.getenv("SQL_HOST")
    
    return {
        "host": SQL_HOST,
        "port": db_config["port"],
        "database": db_config["database"],
        "charset": db_config["charset"],
        "password": SQL_PASSWORDS
    }

# 构建数据库URL
def get_database_url():
    """构建数据库连接URL"""
    db_config = get_database_config()
    return f"mysql+pymysql://dev:{db_config['password']}@{db_config['host']}:{db_config['port']}/{db_config['database']}?charset={db_config['charset']}"

DATABASE_URL = get_database_url()
