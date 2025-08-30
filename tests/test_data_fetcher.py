"""
数据获取器测试
"""

import unittest
import pandas as pd
from unittest.mock import Mock, patch

from src.core.data_fetcher import DataFetcher


class TestDataFetcher(unittest.TestCase):
    """数据获取器测试类"""
    
    def setUp(self):
        """测试前准备"""
        self.fetcher = DataFetcher()
    
    def test_get_available_sources(self):
        """测试获取可用数据源"""
        sources = self.fetcher.get_available_sources()
        expected_sources = ['akshare', 'wind', 'csi', 'cni']
        
        self.assertEqual(set(sources), set(expected_sources))
    
    def test_validate_source(self):
        """测试验证数据源"""
        self.assertTrue(self.fetcher.validate_source('akshare'))
        self.assertTrue(self.fetcher.validate_source('wind'))
        self.assertFalse(self.fetcher.validate_source('invalid_source'))
    
    def test_fetch_all_data_empty_symbols(self):
        """测试获取空符号数据"""
        symbols_by_source = {
            'akshare': {},
            'wind': {},
            'csi': {},
            'cni': {}
        }
        latest_dates = {}
        end_date = "2024-01-01"
        
        result = self.fetcher.fetch_all_data(symbols_by_source, latest_dates, end_date)
        self.assertEqual(result, [])
    
    @patch('src.utils.config_utils.is_data_source_enabled')
    def test_fetch_all_data_disabled_source(self, mock_is_enabled):
        """测试获取禁用数据源的数据"""
        mock_is_enabled.return_value = False
        
        symbols_by_source = {
            'akshare': {'000016.SH': 'sh000016'},
            'wind': {},
            'csi': {},
            'cni': {}
        }
        latest_dates = {'000016.SH': '2024-01-01'}
        end_date = "2024-01-02"
        
        result = self.fetcher.fetch_all_data(symbols_by_source, latest_dates, end_date)
        self.assertEqual(result, [])


if __name__ == '__main__':
    unittest.main()
