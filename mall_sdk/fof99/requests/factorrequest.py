# -*- coding: utf-8 -*-
# 因子相关请求

from .baserequest import BaseRequest


class FactorFutures(BaseRequest):
    """ 提供期货风格因子每日收益率数据 """
    _uri = '/factor/futures'

    def set_params(self, start_date, sub_type='ALL', order=1):
        self['start_date'] = start_date
        self['order'] = order
        self['sub_type'] = sub_type


class FactorStyleCne6(BaseRequest):
    """ 提供CNE6股票风格因子每日收益率数据 """
    _uri = '/factor/style/cne6'

    def set_params(self, start_date, order=1):
        self['start_date'] = start_date
        self['order'] = order


class FactorStyleCne5(BaseRequest):
    """ 提供CNE5股票风格因子每日收益率数据 """
    _uri = '/factor/style/cne5'

    def set_params(self, start_date, order=1):
        self['start_date'] = start_date
        self['order'] = order