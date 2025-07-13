# -*- coding: utf-8 -*-
# 抽象父类

import abc
import hashlib
import urllib.parse

import pandas as pd
import requests


class BaseRequest(abc.ABC):
    """ 请求抽象父类 """
    _uri = None
    _method = 'GET'
    _headers = None
    _params = None
    _filterer = None

    def __init__(self, appid, appkey, gateway=None):
        self.set_gateway(gateway) \
            .set_appid(appid) \
            .set_appkey(appkey)
        self._debug_info = None

    def do_request(self, use_df=False):
        """ 执行请求 """
        url = urllib.parse.urljoin(self._gateway, self._uri)
        params = self._params if isinstance(self._params, dict) else {}
        params.setdefault('app_id', self._appid)
        params = dict(filter(lambda item: True if item[1] is not None else False, params.items()))
        params['sign'] = self._make_sign(params, self._appkey)

        res = None
        if self._method.upper() == 'POST':
            res = self._http_post(url, json=params)
        else:
            res = self._http_get(url, params=params)
        if res and self._filterer:
            res = self._filterer(res)

        if use_df:
            return pd.DataFrame(res)
        return res

    def get_debug_info(self):
        return self._debug_info

    def set_gateway(self, gateway=None):
        self._gateway = gateway if gateway \
            else 'https://mallapi.huofuniu.com'
        self._gateway = self._gateway.rstrip('/')
        return self

    def get_gateway(self):
        return self._gateway

    def set_appid(self, appid):
        self._appid = appid
        return self

    def get_appid(self):
        return self._appid

    def set_appkey(self, appkey):
        self._appkey = appkey
        return self

    def get_appkey(self):
        return self._appkey

    def _make_sign(self, params, sign_key):
        signed_str = ''
        for key in sorted(params):
            if key.lower() == 'sign' \
                    or params[key] is None:
                continue
            signed_str += '&' + key + '=' + \
                          urllib.parse.quote(str(params[key]).encode('utf-8'))
        signed_str = signed_str[1:]
        signed_str += sign_key

        return hashlib.md5(signed_str.encode('utf-8')).hexdigest().lower()

    def _add_param(self, field, value):
        if not self._params:
            self._params = {}
        self._params[field] = value
        return self

    def __setitem__(self, key, value):
        self._add_param(key, value)

    def _add_header(self, field, value):
        if not self._headers:
            self._headers = {}
        self._headers[field] = value
        return self

    def _http_get(self, url, params=None, **kwargs):
        resp = requests.get(url, params=params, **kwargs)
        if resp.status_code != 200:
            self._debug_info = {
                'error_code': resp.status_code,
                'msg': resp.text,
                'data': None
            }
            return

        res = resp.json()
        if ('error_code' not in res) \
            or ('msg' not in res) \
            or ('data' not in res):
            self._debug_info = {
                'error_code': 500,
                'msg': resp.text,
                'data': None
            }
            return
        self._debug_info = res
        if res['error_code'] != 0:
            return
        return res['data']

    def _http_post(self, url, json=None, **kwargs):
        resp = requests.post(url, json=json, **kwargs)
        if resp.status_code != 200:
            self._debug_info = {
                'error_code': resp.status_code,
                'msg': resp.text,
                'data': None
            }
            return

        res = resp.json()
        if ('error_code' not in res) \
                or ('msg' not in res) \
                or ('data' not in res):
            self._debug_info = {
                'error_code': 500,
                'msg': resp.text,
                'data': None
            }
            return
        self._debug_info = res
        if res['error_code'] != 0:
            return
        return res['data']