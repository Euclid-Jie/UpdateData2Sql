# -*- coding: utf-8 -*-
# 测试

# 将fof99目录添加到Python搜索路径【这步很重要，否则执行脚本找不到请求类】
import sys
sys.path.append('..')

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