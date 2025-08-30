"""
项目主配置文件
"""

import os
from pathlib import Path

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent

# 数据目录
DATA_DIR = PROJECT_ROOT / "data"
HOLIDAYS_DIR = DATA_DIR / "holidays"
TEMP_DIR = DATA_DIR / "temp"

# 确保目录存在
DATA_DIR.mkdir(exist_ok=True)
HOLIDAYS_DIR.mkdir(exist_ok=True)
TEMP_DIR.mkdir(exist_ok=True)

# 默认配置
DEFAULT_CONFIG = {
    "database": {
        "host": "localhost",
        "port": 3306,
        "database": "UpdatedData",
        "charset": "utf8"
    },
    "data_sources": {
        "akshare": {
            "enabled": True,
            "timeout": 30
        },
        "wind": {
            "enabled": True,
            "timeout": 30
        },
        "csi": {
            "enabled": True,
            "timeout": 30
        },
        "cni": {
            "enabled": True,
            "timeout": 30
        }
    },
    "logging": {
        "level": "INFO",
        "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    }
}

# 从环境变量获取配置
def get_env_config():
    """从环境变量获取配置"""
    config = DEFAULT_CONFIG.copy()
    
    # 数据库配置
    if os.getenv("DB_HOST"):
        config["database"]["host"] = os.getenv("DB_HOST")
    if os.getenv("DB_PORT"):
        config["database"]["port"] = int(os.getenv("DB_PORT"))
    if os.getenv("DB_NAME"):
        config["database"]["database"] = os.getenv("DB_NAME")
    
    return config
