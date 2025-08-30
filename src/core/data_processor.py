"""
数据处理器核心模块
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Optional
from src.utils.date_utils import is_trading_day


class DataProcessor:
    """数据处理器类"""
    
    def __init__(self):
        self.required_columns = ['date', 'open', 'high', 'low', 'close', 'volume', 'code']
    
    def process_data(self, data_list: List[pd.DataFrame]) -> List[pd.DataFrame]:
        """
        处理数据列表
        
        Args:
            data_list: 原始数据列表
            
        Returns:
            处理后的数据列表
        """
        processed_data = []
        
        for df in data_list:
            if df.empty:
                continue
                
            try:
                processed_df = self._process_single_dataframe(df)
                if not processed_df.empty:
                    processed_data.append(processed_df)
                    
            except Exception as e:
                print(f"处理数据框时出错: {e}")
                continue
        
        return processed_data
    
    def _process_single_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """处理单个数据框"""
        # 检查必需列
        missing_columns = [col for col in self.required_columns if col not in df.columns]
        if missing_columns:
            print(f"缺少必需列: {missing_columns}")
            return pd.DataFrame()
        
        # 复制数据框避免修改原始数据
        processed_df = df.copy()
        
        # 数据类型转换
        processed_df = self._convert_data_types(processed_df)
        
        # 数据清洗
        processed_df = self._clean_data(processed_df)
        
        # 数据验证
        if not self._validate_data(processed_df):
            print("数据验证失败")
            return pd.DataFrame()
        
        return processed_df
    
    def _convert_data_types(self, df: pd.DataFrame) -> pd.DataFrame:
        """转换数据类型"""
        # 日期列转换
        df['date'] = pd.to_datetime(df['date']).dt.strftime('%Y-%m-%d')
        
        # 数值列转换
        numeric_columns = ['open', 'high', 'low', 'close', 'volume']
        for col in numeric_columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        return df
    
    def _clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """清洗数据"""
        # 删除重复行
        df = df.drop_duplicates()
        
        # 删除空值行
        df = df.dropna(subset=['date', 'close'])
        
        # 删除异常值（价格不能为负数）
        df = df[df['close'] > 0]
        df = df[df['open'] > 0]
        df = df[df['high'] > 0]
        df = df[df['low'] > 0]
        
        # 确保high >= low
        df = df[df['high'] >= df['low']]
        
        # 确保high >= open, high >= close
        df = df[df['high'] >= df['open']]
        df = df[df['high'] >= df['close']]
        
        # 确保low <= open, low <= close
        df = df[df['low'] <= df['open']]
        df = df[df['low'] <= df['close']]
        
        return df
    
    def _validate_data(self, df: pd.DataFrame) -> bool:
        """验证数据"""
        if df.empty:
            return False
        
        # 检查必需列
        for col in self.required_columns:
            if col not in df.columns:
                print(f"缺少必需列: {col}")
                return False
        
        # 检查数据类型
        if not pd.api.types.is_datetime64_any_dtype(pd.to_datetime(df['date'])):
            print("日期列格式不正确")
            return False
        
        # 检查数值范围
        if (df['close'] <= 0).any():
            print("收盘价包含非正数")
            return False
        
        return True
    
    def filter_holidays(self, data_list: List[pd.DataFrame], holidays: List[str]) -> List[pd.DataFrame]:
        """过滤节假日数据"""
        filtered_data = []
        
        for df in data_list:
            if df.empty:
                continue
            
            # 过滤掉节假日
            filtered_df = df[~df['date'].isin(holidays)]
            
            if not filtered_df.empty:
                filtered_data.append(filtered_df)
        
        return filtered_data
    
    def merge_data(self, data_list: List[pd.DataFrame]) -> pd.DataFrame:
        """合并数据列表"""
        if not data_list:
            return pd.DataFrame()
        
        # 合并所有数据框
        merged_df = pd.concat(data_list, ignore_index=True)
        
        # 按日期和代码排序
        merged_df = merged_df.sort_values(['date', 'code'])
        
        return merged_df
    
    def calculate_returns(self, df: pd.DataFrame) -> pd.DataFrame:
        """计算收益率"""
        if df.empty:
            return df
        
        # 按代码分组计算收益率
        df = df.copy()
        df['return'] = df.groupby('code')['close'].pct_change()
        
        return df
    
    def calculate_volatility(self, df: pd.DataFrame, window: int = 20) -> pd.DataFrame:
        """计算波动率"""
        if df.empty:
            return df
        
        df = df.copy()
        
        # 计算对数收益率
        df['log_return'] = np.log(df['close'] / df['close'].shift(1))
        
        # 计算滚动波动率
        df['volatility'] = df.groupby('code')['log_return'].rolling(window=window).std().reset_index(0, drop=True)
        
        return df
