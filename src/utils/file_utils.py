"""
文件处理工具模块
"""

import json
import yaml
import pandas as pd
from pathlib import Path
from typing import Any, Dict, Optional


def read_config_file(file_path: str, file_type: str = 'json') -> Dict[str, Any]:
    """读取配置文件"""
    file_path = Path(file_path)
    
    if not file_path.exists():
        raise FileNotFoundError(f"配置文件不存在: {file_path}")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        if file_type.lower() == 'json':
            return json.load(f)
        elif file_type.lower() == 'yaml':
            return yaml.safe_load(f)
        else:
            raise ValueError(f"不支持的文件类型: {file_type}")


def write_config_file(data: Dict[str, Any], file_path: str, file_type: str = 'json'):
    """写入配置文件"""
    file_path = Path(file_path)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        if file_type.lower() == 'json':
            json.dump(data, f, ensure_ascii=False, indent=2)
        elif file_type.lower() == 'yaml':
            yaml.dump(data, f, default_flow_style=False, allow_unicode=True)
        else:
            raise ValueError(f"不支持的文件类型: {file_type}")


def read_data_file(file_path: str, file_type: str = 'csv') -> pd.DataFrame:
    """读取数据文件"""
    file_path = Path(file_path)
    
    if not file_path.exists():
        raise FileNotFoundError(f"数据文件不存在: {file_path}")
    
    if file_type.lower() == 'csv':
        return pd.read_csv(file_path)
    elif file_type.lower() == 'excel':
        return pd.read_excel(file_path)
    elif file_type.lower() == 'json':
        return pd.read_json(file_path)
    else:
        raise ValueError(f"不支持的文件类型: {file_type}")


def write_data_file(data: pd.DataFrame, file_path: str, file_type: str = 'csv'):
    """写入数据文件"""
    file_path = Path(file_path)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    
    if file_type.lower() == 'csv':
        data.to_csv(file_path, index=False, encoding='utf-8')
    elif file_type.lower() == 'excel':
        data.to_excel(file_path, index=False)
    elif file_type.lower() == 'json':
        data.to_json(file_path, orient='records', force_ascii=False, indent=2)
    else:
        raise ValueError(f"不支持的文件类型: {file_type}")


def ensure_directory_exists(directory_path: str):
    """确保目录存在"""
    Path(directory_path).mkdir(parents=True, exist_ok=True)


def get_file_extension(file_path: str) -> str:
    """获取文件扩展名"""
    return Path(file_path).suffix.lower()


def list_files(directory_path: str, pattern: str = "*") -> list:
    """列出目录中的文件"""
    directory = Path(directory_path)
    if not directory.exists():
        return []
    
    return [str(f) for f in directory.glob(pattern)]
