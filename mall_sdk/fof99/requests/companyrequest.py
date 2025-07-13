# -*- coding: utf-8 -*-
# 投资顾问相关

from .baserequest import BaseRequest


class CompanyInfo(BaseRequest):
    """ 提供投资顾问的信息 """
    _uri = '/company/info'

    def set_params(self, reg_code):
        self['code'] = reg_code