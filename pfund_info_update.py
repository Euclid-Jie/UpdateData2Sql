from utils import get_single_company_fund_info
import numpy as np
import sqlalchemy
import os

SQL_PASSWORDS = os.environ["SQL_PASSWORDS"]

if __name__ == "__main__":
    engine = sqlalchemy.create_engine(
        f"mysql+pymysql://dev:{SQL_PASSWORDS}@120.48.57.24:3306/UpdatedData?charset=utf8"
    )
    all_data_df = get_single_company_fund_info(
        begin_date=(
            np.datetime64("now").astype("datetime64[D]") #- np.timedelta64(1, "D")
        ).__str__(),
    )
    if len(all_data_df) > 0:
        all_data_df.to_sql(
            "raw_pfund_info",
            con=engine,
            if_exists="append",
            index=False,
            chunksize=1000,
            method="multi",
        )
        print("pfund_info data updated {} items successfully.".format(len(all_data_df)))
