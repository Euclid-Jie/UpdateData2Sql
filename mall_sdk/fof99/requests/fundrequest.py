# -*- coding: utf-8 -*-
# 私募基金相关请求

from .baserequest import BaseRequest


class FundAdvancedList(BaseRequest):
    """ 根据平台/团队策略，获取基金列表数据 """
    _uri = '/fund/advancedlist'
    _filterer = lambda s, x: x['list']

    def set_params(self, strategy_one='组合策略', strategy_two='不限', type_=1,
                   page=1, pagesize=10, order_by='price_date', order=1):
        self['strategy_one'] = strategy_one
        self['strategy_two'] = strategy_two
        self['type'] = type_
        self['page'] = page
        self['pagesize'] = pagesize
        self['order_by'] = order_by
        self['order'] = order


class FundInfo(BaseRequest):
    """ 提供私募基金基本信息数据 """
    _uri = '/fund/info'

    def set_params(self, reg_code):
        self['reg_code'] = reg_code


class FundPrice(BaseRequest):
    """ 提供私募基金平台净值的数据 """
    _uri = '/price'

    def set_params(self, reg_code, start_date, order_by='price_date', order=1):
        self['reg_code'] = reg_code
        self['start_date'] = start_date
        self['order_by'] = order_by
        self['order'] = order


class FundCompanyPrice(BaseRequest):
    """ 提供私募基金团队净值的数据 """
    _uri = '/company/price'

    def set_params(self, reg_code, start_date, order_by='price_date', order=1):
        self['reg_code'] = reg_code
        self['start_date'] = start_date
        self['order_by'] = order_by
        self['order'] = order


class FundMultiPrice(BaseRequest):
    """ 每次可查询多个基金的平台净值，最多不超过40只 """
    _uri = '/fund/price'

    def set_params(self, reg_code, date_, order_by='price_date', order=1):
        self['reg_code'] = reg_code
        self['date'] = date_
        self['order_by'] = order_by
        self['order'] = order

class PersonFundPrice(BaseRequest):
    """ 提供私募基金平台净值的数据 """
    _uri = '/personal/funds/price'

    def set_params(self, fid, start_date, order_by='price_date', order=1):
        self['fid'] = fid
        self['start_date'] = start_date
        self['order_by'] = order_by
        self['order'] = order