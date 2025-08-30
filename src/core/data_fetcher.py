"""
数据获取器核心模块
"""

import pandas as pd
from typing import Dict, List, Optional
from src.data_sources.akshare_source import AkshareSource
from src.data_sources.wind_source import WindSource
from src.data_sources.csi_source import CSISource
from src.data_sources.cni_source import CNISource
from src.utils.config_utils import is_data_source_enabled


class DataFetcher:
    """数据获取器类"""
    
    def __init__(self):
        self.sources = {
            'akshare': AkshareSource(),
            'wind': WindSource(),
            'csi': CSISource(),
            'cni': CNISource()
        }
    
    def fetch_all_data(
        self,
        symbols_by_source: Dict[str, Dict[str, str]],
        latest_dates: Dict[str, str],
        end_date: str
    ) -> List[pd.DataFrame]:
        """
        从所有数据源获取数据
        
        Args:
            symbols_by_source: 按数据源分组的代码映射
            latest_dates: 最新日期字典
            end_date: 结束日期
            
        Returns:
            所有数据源的合并数据列表
        """
        all_data = []
        
        for source_name, symbols in symbols_by_source.items():
            if not symbols:
                continue
                
            # 检查数据源是否启用
            if not is_data_source_enabled(source_name):
                print(f"数据源 {source_name} 未启用，跳过")
                continue
            
            # 获取数据源实例
            source = self.sources.get(source_name)
            if not source:
                print(f"未找到数据源 {source_name}")
                continue
            
            try:
                # 从该数据源获取数据
                data = source.fetch_index_data(symbols, latest_dates, end_date)
                all_data.extend(data)
                print(f"从 {source_name} 获取了 {len(data)} 个数据框")
                
            except Exception as e:
                print(f"从 {source_name} 获取数据时出错: {e}")
                continue
        
        return all_data
    
    def fetch_akshare_data(
        self, 
        symbols: Dict[str, str], 
        latest_dates: Dict[str, str], 
        end_date: str
    ) -> List[pd.DataFrame]:
        """从akshare获取数据"""
        return self.sources['akshare'].fetch_index_data(symbols, latest_dates, end_date)
    
    def fetch_wind_data(
        self, 
        symbols: Dict[str, str], 
        latest_dates: Dict[str, str], 
        end_date: str
    ) -> List[pd.DataFrame]:
        """从Wind获取数据"""
        return self.sources['wind'].fetch_index_data(symbols, latest_dates, end_date)
    
    def fetch_csi_data(
        self, 
        symbols: Dict[str, str], 
        latest_dates: Dict[str, str], 
        end_date: str
    ) -> List[pd.DataFrame]:
        """从中证获取数据"""
        return self.sources['csi'].fetch_index_data(symbols, latest_dates, end_date)
    
    def fetch_cni_data(
        self, 
        symbols: Dict[str, str], 
        latest_dates: Dict[str, str], 
        end_date: str
    ) -> List[pd.DataFrame]:
        """从国证获取数据"""
        return self.sources['cni'].fetch_index_data(symbols, latest_dates, end_date)
    
    def get_available_sources(self) -> List[str]:
        """获取可用的数据源列表"""
        return list(self.sources.keys())
    
    def validate_source(self, source_name: str) -> bool:
        """验证数据源是否可用"""
        return source_name in self.sources
