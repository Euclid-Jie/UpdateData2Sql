此`repo`只做一件事，把数据更新到云数据库里，目前有部分函数已经设置了使用`actionS`自动更新，但是还有很多是手动，需要逐步做。

在进行开发的时候始终要记得不要提交数据库密码，请使用以下方式：

```python
from config import SQL_PASSWORDS, SQL_HOST

engine = sqlalchemy.create_engine(
    f"mysql+pymysql://dev:{SQL_PASSWORDS}@{SQL_HOST}:3306/UpdatedData?charset=utf8"
)
```

---

介绍下目前的函数，除了第一个都是需要手动更新的

1、`data_update.py`

被`github actions`调用，每天更新一次，目前可以更新基差情况至`UpdatedData`

2、`update_company_info.py`

更新`Euclid.量化私募管理人列表`，依据协会名称从中基协会获取管理人信息，依据登记编号从火富牛中获取管理人信息

3、`update_fund_info.py`

更新`Nav.跟踪产品池`中的产品信息，使用火富牛的公开API，基于备案编码获取

4、`update_wind_data_2_db.py`

更新`UpdatedData.bench_info_wind`数据，从wind中获取数据

5、`utils.py` `FOF99Api` `WindWarehouse.py`

轮子函数
