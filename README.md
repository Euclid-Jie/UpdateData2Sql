# UpdateData2Sql

## 项目简介

`UpdateData2Sql` 是一个用于从多个数据源（如 akshare、Wind、中证、国证等）获取指数数据并更新到数据库的 Python 项目。该项目通过自动化脚本实现数据的定期更新，确保数据库中的数据始终保持最新状态。

## 项目结构

```
UpdateData2Sql/
├── src/                          # 源代码目录
│   ├── core/                     # 核心功能模块
│   │   ├── __init__.py
│   │   ├── database.py           # 数据库连接和操作
│   │   ├── data_fetcher.py       # 数据获取器
│   │   └── data_processor.py     # 数据处理器
│   ├── data_sources/             # 数据源模块
│   │   ├── __init__.py
│   │   ├── akshare_source.py     # akshare数据源
│   │   ├── wind_source.py        # Wind数据源
│   │   ├── csi_source.py         # 中证数据源
│   │   └── cni_source.py         # 国证数据源
│   ├── utils/                    # 工具模块
│   │   ├── __init__.py
│   │   ├── date_utils.py         # 日期处理工具
│   │   ├── file_utils.py         # 文件处理工具
│   │   └── config_utils.py       # 配置工具
│   └── scripts/                  # 脚本模块
│       ├── __init__.py
│       ├── index_updater.py      # 指数更新脚本
│       ├── fund_updater.py       # 基金更新脚本
│       └── company_updater.py    # 公司信息更新脚本
├── config/                       # 配置文件目录
│   ├── __init__.py
│   ├── settings.py               # 主配置文件
│   └── database.py               # 数据库配置
├── data/                         # 数据文件目录
│   ├── holidays/                 # 节假日数据
│   │   └── Chinese_special_holiday.txt
│   └── temp/                     # 临时数据文件
├── tests/                        # 测试目录
│   ├── __init__.py
│   ├── test_data_fetcher.py
│   └── test_database.py
├── docs/                         # 文档目录
│   ├── api.md
│   └── deployment.md
├── requirements.txt              # 项目依赖
├── setup.py                      # 项目安装配置
└── README.md                     # 项目说明文档
```

## 功能特性

- 支持从多种数据源获取指数数据。
- 自动判断交易日，避免非交易日运行。
- 数据处理流程包括数据拉取、清洗、存储等步骤。
- 使用 GitHub Actions 实现自动化更新，确保数据每日更新。

## 使用说明

### 环境依赖

```bash
pip install -r requirements.txt
```

### 配置文件

确保项目根目录下存在以下配置文件：

- `data/holidays/Chinese_special_holiday.txt`：包含中国特殊节假日信息，用于判断交易日。

### 数据库配置

数据库连接信息需在 `config/database.py` 中配置。

## 自动化更新

### GitHub Actions 配置

本项目使用 GitHub Actions 实现自动化更新。以下是自动化更新的主要步骤：

1. **触发条件**：工作流每天定时触发（可在 `.github/workflows/update_data.yml` 中配置触发时间）。
2. **运行脚本**：工作流拉取最新代码后，运行 `src/scripts/index_updater.py` 脚本。
3. **更新数据库**：脚本完成数据拉取和更新操作。

### 配置步骤

1. 在项目根目录下创建 `.github/workflows/update_data.yml` 文件，内容如下：

```yaml
name: Update Data

on:
  schedule:
    - cron: '0 2 * * *' # 每天凌晨 2 点运行
  workflow_dispatch: # 手动触发

jobs:
  update-data:
    runs-on: ubuntu-latest

    steps:
    - name: Checkout code
      uses: actions/checkout@v3

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: 3.8

    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt

    - name: Run update script
      run: python src/scripts/index_updater.py
```

2. 将 `.github/workflows/update_data.yml` 文件提交到仓库。

3. 确保数据库连接信息和相关配置文件已正确设置。

### 手动触发

除了定时触发，GitHub Actions 还支持手动触发工作流。进入 GitHub 仓库的 Actions 页面，选择 `Update Data` 工作流，点击 `Run workflow` 即可手动运行。

## 开发指南

### 添加新的数据源

1. 在 `src/data_sources/` 目录下创建新的数据源模块
2. 实现必要的数据获取方法
3. 在 `src/core/data_fetcher.py` 中注册新的数据源
4. 更新配置文件

### 运行测试

```bash
python -m pytest tests/
```

### 代码规范

项目遵循 PEP 8 代码规范，建议使用 black 进行代码格式化：

```bash
pip install black
black src/
```

