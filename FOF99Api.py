import requests
from mall_sdk.fof99 import (
    PersonFundPrice,
    FundInfo,
    FundPrice,
    FundCompanyPrice,
    GmFundPrice,
    CompanyInfo,
)
import pandas as pd
from config import APPID, APPKEY


class FOF99Api:
    appid: str = APPID
    appkey: str = APPKEY
    token: str = ""

    def __init__(self):
        pass

    def get_fund_info(self, reg_code: str = "SVZ009"):
        req = FundInfo(self.appid, self.appkey)  # 请求对
        req.set_params(reg_code)
        res = req.do_request(use_df=False)
        return res

    def get_company_info(self, reg_code: str = "P1002305"):
        req = CompanyInfo(self.appid, self.appkey)  # 请求对
        req.set_params(reg_code)
        res = req.do_request(use_df=False)
        return res

    def get_fund_price(
        self,
        reg_code: str = "SVZ009",
        start_date: str = "2010-01-01",
    ):
        req = FundPrice(self.appid, self.appkey)  # 请求对
        req.set_params(reg_code=reg_code, start_date=start_date)
        res = req.do_request(use_df=True)
        return res

    def get_person_fund_price(
        self,
        fid: str = "381719",
        start_date: str = "2010-01-01",
    ):
        req = PersonFundPrice(self.appid, self.appkey)  # 请求对
        req.set_params(fid=fid, start_date=start_date)
        res = req.do_request(use_df=True)
        return res

    def get_company_price(
        self,
        reg_code: str = "JX919A",
        start_date: str = "2010-01-01",
    ):
        req = FundCompanyPrice(self.appid, self.appkey)  # 请求对
        req.set_params(reg_code=reg_code, start_date=start_date)
        res = req.do_request(use_df=True)
        return res

    def get_public_fund_price(
        self,
        reg_code="022461",
        start_date: str = "2010-01-01",
    ) -> pd.DataFrame:
        req = GmFundPrice(self.appid, self.appkey)  # 请求对
        req.set_params(str(reg_code).zfill(6), start_date=start_date)
        res = req.do_request(use_df=True)
        return res

    def get_company_info_from_code(self, comp_code) -> dict:
        url = f"https://api.huofuniu.com/newgoapi/company/advancedlist?token={self.token}&keyValue={comp_code}&member_type=%E4%B8%8D%E9%99%90&fund_num=-1&scale=0&found_date=0&active=1&company_manager_active=-1&page=1&pagesize=20&advise_type=0&order_by=fund_num&order=1&isReport=0"
        headers = {
            "access-token": self.token,
        }
        annlysis_data = requests.get(url=url, headers=headers)
        try:
            company_info = annlysis_data.json()["data"]["list"][0]
        except:
            raise ValueError("请检查token是否过期")
        return company_info
