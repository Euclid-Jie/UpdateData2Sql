# 部署文档

## 概述

本文档描述了如何部署和配置 UpdateData2Sql 项目。

## 环境要求

### Python 版本

- Python 3.8 或更高版本

### 依赖包

项目依赖包列表见 `requirements.txt` 文件。

## 安装步骤

### 1. 克隆项目

```bash
git clone <repository_url>
cd UpdateData2Sql
```

### 2. 创建虚拟环境

```bash
# 使用 venv
python -m venv .venv

# 激活虚拟环境
# Windows
.venv\Scripts\activate

# Linux/Mac
source .venv/bin/activate
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

### 4. 配置数据库

编辑 `config/database.py` 文件，设置数据库连接信息：

```python
SQL_PASSWORDS = "your_actual_password"
SQL_HOST = "your_database_host"
```

或者设置环境变量：

```bash
export SQL_PASSWORDS="your_actual_password"
export SQL_HOST="your_database_host"
```

### 5. 配置数据源

编辑 `config/settings.py` 文件，根据需要启用或禁用数据源：

```python
DEFAULT_CONFIG = {
    "data_sources": {
        "akshare": {
            "enabled": True,
            "timeout": 30
        },
        "wind": {
            "enabled": False,  # 禁用 Wind 数据源
            "timeout": 30
        },
        # ...
    }
}
```

## 运行项目

### 手动运行

```bash
# 运行指数更新
python src/scripts/index_updater.py

# 运行基金更新
python src/scripts/fund_updater.py

# 运行公司信息更新
python src/scripts/company_updater.py
```

### 自动化运行

#### GitHub Actions

1. 在项目根目录创建 `.github/workflows/update_data.yml` 文件
2. 配置定时触发和手动触发
3. 设置必要的环境变量

#### Cron 任务

```bash
# 编辑 crontab
crontab -e

# 添加定时任务（每天凌晨 2 点运行）
0 2 * * * cd /path/to/UpdateData2Sql && python src/scripts/index_updater.py
```

## 配置说明

### 数据库配置

- `host`: 数据库主机地址
- `port`: 数据库端口（默认 3306）
- `database`: 数据库名称
- `charset`: 字符集（默认 utf8）

### 数据源配置

每个数据源可以配置以下参数：

- `enabled`: 是否启用该数据源
- `timeout`: 请求超时时间（秒）

### 日志配置

- `level`: 日志级别（INFO, DEBUG, WARNING, ERROR）
- `format`: 日志格式

## 监控和维护

### 日志查看

项目运行时会输出详细的日志信息，包括：

- 数据获取状态
- 数据处理进度
- 错误信息

### 数据验证

定期检查数据库中的数据：

```sql
-- 检查最新数据日期
SELECT code, MAX(date) as latest_date 
FROM bench_basic_data 
GROUP BY code;

-- 检查数据完整性
SELECT COUNT(*) as total_records 
FROM bench_basic_data;
```

### 性能优化

1. **数据库索引**: 为常用查询字段创建索引
2. **批量处理**: 使用批量插入提高性能
3. **连接池**: 配置数据库连接池
4. **缓存**: 对频繁访问的数据进行缓存

## 故障排除

### 常见问题

1. **数据库连接失败**
   - 检查数据库配置
   - 确认网络连接
   - 验证用户权限

2. **数据源访问失败**
   - 检查 API 密钥
   - 确认网络连接
   - 查看数据源状态

3. **数据格式错误**
   - 检查数据源返回格式
   - 验证数据处理逻辑
   - 查看错误日志

### 调试模式

启用调试模式获取更详细的日志：

```python
# 在配置中设置日志级别为 DEBUG
DEFAULT_CONFIG["logging"]["level"] = "DEBUG"
```

## 备份和恢复

### 数据备份

```bash
# 备份数据库
mysqldump -u username -p database_name > backup.sql

# 备份配置文件
cp -r config/ config_backup/
```

### 数据恢复

```bash
# 恢复数据库
mysql -u username -p database_name < backup.sql

# 恢复配置文件
cp -r config_backup/ config/
```

## 安全考虑

1. **API 密钥管理**: 使用环境变量存储敏感信息
2. **数据库安全**: 限制数据库访问权限
3. **网络安全**: 使用 HTTPS 进行数据传输
4. **日志安全**: 避免在日志中记录敏感信息
