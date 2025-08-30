"""
数据库测试
"""

import unittest
import pandas as pd
from unittest.mock import Mock, patch

from src.core.database import get_latest_dates, update_latest_dates, get_source_info


class TestDatabase(unittest.TestCase):
    """数据库测试类"""
    
    def setUp(self):
        """测试前准备"""
        self.mock_engine = Mock()
        self.mock_conn = Mock()
        self.mock_engine.connect.return_value.__enter__.return_value = self.mock_conn
    
    def test_get_latest_dates(self):
        """测试获取最新日期"""
        # 模拟查询结果
        mock_df = pd.DataFrame({
            'code': ['000016.SH', '000852.SH'],
            'latest_date': ['2024-01-01', '2024-01-02']
        })
        
        with patch('pandas.read_sql', return_value=mock_df):
            result = get_latest_dates(self.mock_engine, 'test_table')
            
            self.assertEqual(len(result), 2)
            self.assertEqual(result.iloc[0]['code'], '000016.SH')
            self.assertEqual(result.iloc[1]['code'], '000852.SH')
    
    def test_get_source_info(self):
        """测试获取数据源信息"""
        # 模拟查询结果
        mock_df = pd.DataFrame({
            'code': ['000016.SH'],
            'updated_date': ['2024-01-01'],
            'indexID': ['test_id'],
            'source': ['ak']
        })
        
        with patch('pandas.read_sql', return_value=mock_df):
            result = get_source_info(
                self.mock_engine, 
                'test_info_table', 
                additional_columns=['indexID', 'source']
            )
            
            self.assertEqual(len(result), 1)
            self.assertEqual(result.iloc[0]['code'], '000016.SH')
            self.assertEqual(result.iloc[0]['source'], 'ak')
    
    def test_get_source_info_no_additional_columns(self):
        """测试获取数据源信息（无额外列）"""
        # 模拟查询结果
        mock_df = pd.DataFrame({
            'code': ['000016.SH'],
            'updated_date': ['2024-01-01']
        })
        
        with patch('pandas.read_sql', return_value=mock_df):
            result = get_source_info(self.mock_engine, 'test_info_table')
            
            self.assertEqual(len(result), 1)
            self.assertEqual(result.iloc[0]['code'], '000016.SH')
            self.assertNotIn('indexID', result.columns)


if __name__ == '__main__':
    unittest.main()
