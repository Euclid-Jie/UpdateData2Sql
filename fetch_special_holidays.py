import pandas as pd
import sqlalchemy
from utils import connect_to_database

engine = connect_to_database()
query = 'SELECT date FROM Chinese_special_holiday'
holidays = pd.read_sql(query, engine)
holidays.to_csv("Chinese_special_holiday.txt", index=False, header=False)
print("成功更新Chinese_special_holiday.txt")