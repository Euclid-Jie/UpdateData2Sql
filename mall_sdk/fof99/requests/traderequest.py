# -*- coding: utf-8 -*-
# 交易相关

from .baserequest import BaseRequest


class FundBuyInfo(BaseRequest):
    """ 提供【投资-直投产品】列表中公/私募基金的交易记录数据 """
    _uri = '/fund/buy/info'

    def set_params(self, code, start_date=None, end_date=None):
        self['code'] = code
        self['start_time'] = start_date
        self['end_time'] = end_date