# API 文档

## 概述

本文档描述了 UpdateData2Sql 项目的 API 接口。

## 核心模块

### DataFetcher

数据获取器，负责从各种数据源获取数据。

#### 方法

- `fetch_all_data(symbols_by_source, latest_dates, end_date)`: 从所有数据源获取数据
- `fetch_akshare_data(symbols, latest_dates, end_date)`: 从 akshare 获取数据
- `fetch_wind_data(symbols, latest_dates, end_date)`: 从 Wind 获取数据
- `fetch_csi_data(symbols, latest_dates, end_date)`: 从中证获取数据
- `fetch_cni_data(symbols, latest_dates, end_date)`: 从国证获取数据

### DataProcessor

数据处理器，负责数据清洗、验证和处理。

#### 方法

- `process_data(data_list)`: 处理数据列表
- `filter_holidays(data_list, holidays)`: 过滤节假日数据
- `merge_data(data_list)`: 合并数据列表
- `calculate_returns(df)`: 计算收益率
- `calculate_volatility(df, window)`: 计算波动率

### IndexUpdater

指数更新器，负责指数数据的完整更新流程。

#### 方法

- `run()`: 运行指数更新流程

## 数据源模块

### AkshareSource

akshare 数据源实现。

#### 方法

- `fetch_index_data(symbols, latest_dates, end_date)`: 获取指数数据
- `get_available_indices()`: 获取可用指数列表
- `validate_code(code)`: 验证代码是否有效

### WindSource

Wind 数据源实现。

#### 方法

- `fetch_index_data(symbols, latest_dates, end_date)`: 获取指数数据
- `get_available_indices()`: 获取可用指数列表
- `validate_code(code)`: 验证代码是否有效

## 工具模块

### 日期工具 (date_utils)

- `load_holidays(holiday_path)`: 加载节假日数据
- `is_trading_day(date, holidays)`: 判断是否为交易日
- `get_trading_dates(start_date, end_date, holidays)`: 获取交易日列表
- `format_date(date, format_str)`: 格式化日期

### 文件工具 (file_utils)

- `read_config_file(file_path, file_type)`: 读取配置文件
- `write_config_file(data, file_path, file_type)`: 写入配置文件
- `read_data_file(file_path, file_type)`: 读取数据文件
- `write_data_file(data, file_path, file_type)`: 写入数据文件

### 配置工具 (config_utils)

- `get_config(key)`: 获取配置值
- `set_config(key, value)`: 设置配置值
- `get_database_config()`: 获取数据库配置
- `is_data_source_enabled(source_name)`: 检查数据源是否启用

## 数据库模块

### 数据库操作

- `connect_to_database()`: 连接数据库
- `get_latest_dates(engine, table_name)`: 获取最新日期
- `update_latest_dates(engine, latest_dates_df, info_table_name)`: 更新最新日期
- `get_source_info(engine, info_table_name, additional_columns)`: 获取数据源信息
- `save_data_to_database(data_list, table_name, engine, holidays)`: 保存数据到数据库

## 使用示例

### 基本使用

```python
from src.scripts.index_updater import IndexUpdater

# 创建更新器并运行
updater = IndexUpdater()
updater.run()
```

### 自定义数据获取

```python
from src.core.data_fetcher import DataFetcher
from src.core.data_processor import DataProcessor

# 创建数据获取器和处理器
fetcher = DataFetcher()
processor = DataProcessor()

# 定义符号映射
symbols = {'000016.SH': 'sh000016'}

# 获取数据
data = fetcher.fetch_akshare_data(symbols, {}, '2024-01-01')

# 处理数据
processed_data = processor.process_data(data)
```

### 配置管理

```python
from src.utils.config_utils import get_config, set_config

# 获取配置
db_config = get_config('database')

# 设置配置
set_config('database.host', 'localhost')
```
