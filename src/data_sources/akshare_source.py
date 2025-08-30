"""
akshare数据源模块
"""

import pandas as pd
import akshare as ak
from datetime import datetime
from typing import Dict, List, Optional
from src.utils.date_utils import is_trading_day


class AkshareSource:
    """akshare数据源类"""
    
    def __init__(self, timeout: int = 30):
        self.timeout = timeout
    
    def fetch_index_data(
        self, 
        symbols: Dict[str, str], 
        latest_dates: Dict[str, str], 
        end_date: str
    ) -> List[pd.DataFrame]:
        """
        获取指数数据
        
        Args:
            symbols: 代码映射字典 {code: akshare_code}
            latest_dates: 最新日期字典 {code: latest_date}
            end_date: 结束日期
            
        Returns:
            数据列表
        """
        data_list = []
        
        for code, akshare_code in symbols.items():
            try:
                # 获取最新日期
                latest_date = latest_dates.get(code, "2020-01-01")
                
                # 获取数据
                df = self._fetch_single_index(akshare_code, latest_date, end_date)
                
                if not df.empty:
                    # 添加代码列
                    df['code'] = code
                    data_list.append(df)
                    print(f"成功获取 {code} 的数据，共 {len(df)} 条")
                else:
                    print(f"未获取到 {code} 的新数据")
                    
            except Exception as e:
                print(f"获取 {code} 数据时出错: {e}")
                continue
        
        return data_list
    
    def _fetch_single_index(
        self, 
        akshare_code: str, 
        start_date: str, 
        end_date: str
    ) -> pd.DataFrame:
        """获取单个指数的数据"""
        try:
            # 使用akshare获取指数数据
            df = ak.stock_zh_index_daily(symbol=akshare_code)
            
            # 重命名列
            df = df.rename(columns={
                'date': 'date',
                'open': 'open',
                'high': 'high', 
                'low': 'low',
                'close': 'close',
                'volume': 'volume'
            })
            
            # 过滤日期范围
            df['date'] = pd.to_datetime(df['date'])
            start_dt = pd.to_datetime(start_date)
            end_dt = pd.to_datetime(end_date)
            
            df = df[(df['date'] > start_dt) & (df['date'] <= end_dt)]
            
            # 格式化日期
            df['date'] = df['date'].dt.strftime('%Y-%m-%d')
            
            # 选择需要的列
            columns = ['date', 'open', 'high', 'low', 'close', 'volume']
            df = df[columns]
            
            return df
            
        except Exception as e:
            print(f"获取 {akshare_code} 数据失败: {e}")
            return pd.DataFrame()
    
    def get_available_indices(self) -> List[str]:
        """获取可用的指数列表"""
        try:
            # 这里可以根据需要实现获取可用指数列表的逻辑
            # 暂时返回一些常用的指数代码
            return [
                "sh000016",  # 上证50
                "sh000852",  # 中证1000
                "sh000905",  # 中证500
                "sh000300",  # 沪深300
            ]
        except Exception as e:
            print(f"获取可用指数列表失败: {e}")
            return []
    
    def validate_code(self, code: str) -> bool:
        """验证代码是否有效"""
        try:
            # 尝试获取少量数据来验证代码
            df = ak.stock_zh_index_daily(symbol=code)
            return not df.empty
        except:
            return False
