"""
配置模块
包含项目配置和数据库配置
"""

from .settings import *
from .database import *

__all__ = [
    'SQL_PASSWORDS',
    'SQL_HOST',
    'DATABASE_URL',
    'DEFAULT_CONFIG'
]
