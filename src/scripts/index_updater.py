"""
指数更新脚本
重构自原来的index_update.py
"""

import pandas as pd
from datetime import datetime
from typing import Dict, List

from src.core.database import (
    connect_to_database,
    get_latest_dates,
    update_latest_dates,
    get_source_info,
    save_data_to_database
)
from src.core.data_fetcher import DataFetcher
from src.core.data_processor import DataProcessor
from src.utils.date_utils import load_holidays


class IndexUpdater:
    """指数更新器类"""
    
    def __init__(self):
        self.data_fetcher = DataFetcher()
        self.data_processor = DataProcessor()
        
        # 定义表名
        self.table_name = "bench_basic_data"
        self.info_name = "bench_info_wind"
        
        # 节假日文件路径
        self.holiday_path = "data/holidays/Chinese_special_holiday.txt"
    
    def run(self):
        """运行指数更新流程"""
        print("开始指数数据更新...")
        
        try:
            # 1. 加载节假日数据
            holidays = load_holidays(self.holiday_path)
            print(f"加载了 {len(holidays)} 个节假日")
            
            # 2. 连接数据库
            engine = connect_to_database()
            
            # 3. 获取最新日期信息
            latest_dates_df = get_latest_dates(engine, self.table_name)
            update_latest_dates(engine, latest_dates_df, self.info_name)
            
            # 4. 获取数据源信息
            info_df = get_source_info(
                engine, self.info_name, additional_columns=["indexID", "source"]
            )
            info_df["updated_date"] = pd.to_datetime(info_df["updated_date"])
            
            # 5. 构建代码映射
            symbols_by_source = self._build_symbols_mapping(info_df)
            
            # 6. 获取数据
            all_new_data = self._fetch_all_data(symbols_by_source, info_df)
            
            # 7. 处理数据
            processed_data = self.data_processor.process_data(all_new_data)
            
            # 8. 保存数据到数据库
            save_data_to_database(processed_data, self.table_name, engine, holidays)
            
            # 9. 更新最新日期
            latest_dates_df = get_latest_dates(engine, self.table_name)
            update_latest_dates(engine, latest_dates_df, self.info_name)
            
            print("指数数据更新完成！")
            
        except Exception as e:
            print(f"指数更新过程中出错: {e}")
            raise
    
    def _build_symbols_mapping(self, info_df: pd.DataFrame) -> Dict[str, Dict[str, str]]:
        """构建按数据源分组的代码映射"""
        symbols_by_source = {
            'akshare': {},
            'wind': {},
            'csi': {},
            'cni': {}
        }
        
        for _, row in info_df.iterrows():
            code = row["code"]
            source = row["source"]
            
            if source == "ak":
                symbols_by_source['akshare'][code] = code[-2:].lower() + code[0:6]
            elif source == "wind":
                symbols_by_source['wind'][code] = row["indexID"]
            elif source == "CSI":
                symbols_by_source['csi'][code] = code[0:6]
            elif source == "CNI":
                symbols_by_source['cni'][code] = code[0:6]
        
        # 打印获取到的指数代码信息
        print("获取到的指数代码信息：")
        for source, symbols in symbols_by_source.items():
            if symbols:
                print(f"{source}: {symbols}")
        
        return symbols_by_source
    
    def _fetch_all_data(
        self, 
        symbols_by_source: Dict[str, Dict[str, str]], 
        info_df: pd.DataFrame
    ) -> List[pd.DataFrame]:
        """获取所有数据源的数据"""
        today_str = datetime.now().strftime("%Y%m%d")
        latest_dates_dict = info_df.set_index("code")["updated_date"].to_dict()
        
        # 使用数据获取器获取所有数据
        all_new_data = self.data_fetcher.fetch_all_data(
            symbols_by_source, latest_dates_dict, today_str
        )
        
        # 过滤空数据框
        all_new_data = [df for df in all_new_data if not df.empty]
        
        return all_new_data


def main():
    """主函数"""
    updater = IndexUpdater()
    updater.run()


if __name__ == "__main__":
    main()
