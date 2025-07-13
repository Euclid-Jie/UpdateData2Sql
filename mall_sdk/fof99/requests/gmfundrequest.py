# -*- coding: utf-8 -*-
# 公募基金相关请求

from .baserequest import BaseRequest


class GmFundInfo(BaseRequest):
    """ 提供公募基金基本信息数据 """
    _uri = '/gm/detail'

    def set_params(self, reg_code):
        self['reg_code'] = reg_code


class GmFundPrice(BaseRequest):
    """ 提供公募基金净值的数据 """
    _uri = '/gm/price'

    def set_params(self, reg_code, start_date, end_date=None, order_by='price_date', order=1):
        self['reg_code'] = reg_code
        self['start_date'] = start_date
        self['end_date'] = end_date
        self['order_by'] = order_by
        self['order'] = order


class GmFundBatchPrice(BaseRequest):
    """ 每次可查询多个基金的净值，最多不超过40只 """
    _uri = '/gm/batch/price'

    def set_params(self, reg_code, price_date, order_by='nav', order=1):
        self['reg_code'] = reg_code
        self['date'] = price_date
        self['order_by'] = order_by
        self['order'] = order