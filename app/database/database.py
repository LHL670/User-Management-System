from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# SQLite 資料庫檔案位址
SQLALCHEMY_DATABASE_URL = "sqlite:///./sql_app.db"

# 建立資料庫引擎
# connect_args={"check_same_thread": False} 是 SQLite 專用的設定
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# 建立 Session (資料庫連線會話)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# ORM 模型的基類
Base = declarative_base()

# Dependency: 用於在 API 請求中取得資料庫連線
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()