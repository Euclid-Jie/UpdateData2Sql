# -*- coding: utf-8 -*-
# 组合（模拟&&实盘）相关

from .baserequest import BaseRequest


class FoCombiPrice(BaseRequest):
    """ 提供团队/我的实盘组合净值的数据 """
    _uri = '/fo_combi/price'

    def set_params(self, combi_id):
        self['id'] = combi_id


class CombiPrice(BaseRequest):
    """ 提供团队/我的模拟组合净值的数据 """
    _uri = '/combi/price'

    def set_params(self, combi_id):
        self['id'] = combi_id
