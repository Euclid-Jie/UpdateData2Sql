# 火富牛SDK

## SDK请求类

```
    FactorFutures：提供期货风格因子每日收益率数据
    FactorStyleCne6：提供CNE6股票风格因子每日收益率数据
    FactorStyleCne5：提供CNE5股票风格因子每日收益率数据
    
    IndexPrice：提供基准指数的行情数据查询
    IndexBatchPrice：多指数行情查询
    IndexStockAmt：提供股票指数的成交额数据
    IndexStockTurn：提供股票指数的换手率数据
    IndexStockPE：提供股票指数的PE（TTM）中位数数据
    
    FundAdvancedList：根据平台/团队策略，获取基金列表数据
    FundInfo：提供私募基金基本信息数据
    FundPrice：提供私募基金平台净值的数据
    FundCompanyPrice：提供私募基金团队净值的数据
    FundMultiPrice：每次可查询多个基金的平台净值，最多不超过40只

    GmFundInfo：提供公募基金基本信息数据
    GmFundPrice：提供公募基金净值的数据
    GmFundBatchPrice：公募基金多基金净值
    
    FoCombiPrice：提供团队/我的实盘组合净值的数据
    CombiPrice：提供团队/我的模拟组合净值的数据
    
    CompanyInfo：提供投资顾问的信息
    
    FundBuyInfo：提供【投资-直投产品】列表中公/私募基金的交易记录数据
```


## 安装依赖类库

```shell
    # 进入包含【requirements.txt】文件的目录执行下面命令
    pip install -r requirements.txt --trusted-host mirrors.aliyun.com \
        --index-url "https://mirrors.aliyun.com/pypi/simple/" 
```


## SDK使用示例

```python

    # 将fof99目录添加到Python搜索路径【这步很重要，否则执行脚本找不到请求类】
    import sys
    sys.path.append(r'E:\path\to\mall_sdk')
    
    # 1、引入请求类
    from fof99 import FundBuyInfo
    
    # 2、创建请求对象
    appid = '应用ID，从火富牛API商城获取'
    appkey = '应用密钥，从火富牛API商城获取'
    req = FundBuyInfo(appid, appkey) # 请求对象
    
    # 3、设置请求参数，参考API文档
    req.set_params('SEE186')
    
    # 4、发起请求， use_df=True表示结果返回pandas.DataFrame对象；use_df=False表示结果返回Python列表
    res = req.do_request(use_df=True)
    
    # 5、结果处理
    print(res) # 打印结果
    print(req.get_debug_info()) # 打印API响应参数，用于接口调试
```

