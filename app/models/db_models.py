from sqlalchemy import Column, Integer, String
from ..database.database import Base

class User(Base):
    __tablename__ = "users"

    # 定義欄位
    # 加一個 id 作為 Primary Key，雖然你的需求是用 name 當識別，
    # 但資料庫通常習慣有個數值型 id，name 設為 unique 即可。
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    age = Column(Integer)