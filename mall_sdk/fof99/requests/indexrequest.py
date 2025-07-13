# -*- coding: utf-8 -*-
# 指数相关请求

from .baserequest import BaseRequest


class IndexPrice(BaseRequest):
    """ 提供基准指数的行情数据查询 """
    _uri = '/index/price'

    def set_params(self, reg_code, start_date, order_by='price_date', order=1):
        self['reg_code'] = reg_code
        self['start_date'] = start_date
        self['order_by'] = order_by
        self['order'] = order


class IndexBatchPrice(BaseRequest):
    """ 每次可查询多个指数的行情数据，最多不超过40只 """
    _uri = '/index/batch/price'

    def set_params(self, reg_code, price_date, order_by='nav', order=1):
        self['reg_code'] = reg_code
        self['date'] = price_date
        self['order_by'] = order_by
        self['order'] = order


class IndexStockAmt(BaseRequest):
    """ 提供股票指数的成交额数据 """
    _uri = '/index/stockAmt'

    def set_params(self, start_date, end_date=None):
        self['start_date'] = start_date
        self['end_date'] = end_date


class IndexStockTurn(BaseRequest):
    """ 提供股票指数的换手率数据 """
    _uri = '/index/stockTurn'

    def set_params(self, start_date, end_date=None):
        self['start_date'] = start_date
        self['end_date'] = end_date


class IndexStockPE(BaseRequest):
    """ 提供股票指数的PE（TTM）中位数数据 """
    _uri = '/index/stockPe'

    def set_params(self, start_date, end_date=None):
        self['start_date'] = start_date
        self['end_date'] = end_date