"""
配置工具模块
"""

import os
from typing import Any, Dict, Optional
from config.settings import DEFAULT_CONFIG, get_env_config


def get_config(key: Optional[str] = None) -> Any:
    """获取配置值"""
    config = get_env_config()
    
    if key is None:
        return config
    
    # 支持嵌套键，如 "database.host"
    keys = key.split('.')
    value = config
    
    for k in keys:
        if isinstance(value, dict) and k in value:
            value = value[k]
        else:
            return None
    
    return value


def set_config(key: str, value: Any):
    """设置配置值（仅在内存中，不会持久化）"""
    config = get_env_config()
    
    # 支持嵌套键，如 "database.host"
    keys = key.split('.')
    current = config
    
    # 导航到最后一个键的父级
    for k in keys[:-1]:
        if k not in current:
            current[k] = {}
        current = current[k]
    
    # 设置值
    current[keys[-1]] = value


def get_database_config() -> Dict[str, Any]:
    """获取数据库配置"""
    return get_config("database")


def get_data_source_config(source_name: str) -> Dict[str, Any]:
    """获取指定数据源的配置"""
    return get_config(f"data_sources.{source_name}")


def is_data_source_enabled(source_name: str) -> bool:
    """检查数据源是否启用"""
    config = get_data_source_config(source_name)
    return config.get("enabled", False) if config else False


def get_logging_config() -> Dict[str, Any]:
    """获取日志配置"""
    return get_config("logging")


def get_environment_variable(key: str, default: Any = None) -> Any:
    """获取环境变量"""
    return os.getenv(key, default)


def set_environment_variable(key: str, value: str):
    """设置环境变量"""
    os.environ[key] = value


def load_config_from_file(file_path: str) -> Dict[str, Any]:
    """从文件加载配置"""
    from .file_utils import read_config_file
    
    try:
        file_type = file_path.split('.')[-1].lower()
        if file_type not in ['json', 'yaml', 'yml']:
            file_type = 'json'
        
        return read_config_file(file_path, file_type)
    except Exception as e:
        print(f"加载配置文件失败: {e}")
        return {}


def merge_configs(base_config: Dict[str, Any], override_config: Dict[str, Any]) -> Dict[str, Any]:
    """合并配置"""
    result = base_config.copy()
    
    for key, value in override_config.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = merge_configs(result[key], value)
        else:
            result[key] = value
    
    return result
