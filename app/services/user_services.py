import pandas as pd
import io
from sqlalchemy.orm import Session
from ..models.db_models import User  # 匯入 DB 模型
from ..models.models import UserCreate, UserUpdate # 匯入 Pydantic 模型

class UserService:
    @staticmethod
    def get_all_users(db: Session):
        # SQL: SELECT * FROM users;
        return db.query(User).all()

    @staticmethod
    def create_user(db: Session, user: UserCreate):
        # 檢查重複 (SQL: SELECT * FROM users WHERE name = ... LIMIT 1)
        existing_user = db.query(User).filter(User.name == user.name).first()
        if existing_user:
            return None
        
        # 建立 DB 物件
        db_user = User(name=user.name, age=user.age)
        db.add(db_user)
        db.commit()      # 提交交易
        db.refresh(db_user) # 重新載入資料 (取得 id)
        return db_user

    @staticmethod
    def update_user(db: Session, name: str, user_update: UserUpdate):
        # 查詢
        db_user = db.query(User).filter(User.name == name).first()
        if not db_user:
            return None
        
        # 更新
        db_user.age = user_update.age
        db.commit()
        db.refresh(db_user)
        return db_user

    @staticmethod
    def delete_user_by_name(db: Session, name: str) -> bool:
        db_user = db.query(User).filter(User.name == name).first()
        if not db_user:
            return False
        
        db.delete(db_user)
        db.commit()
        return True

    @staticmethod
    async def process_csv_upload(db: Session, file_content: bytes) -> list:
        try:
            # 讀取 CSV
            df = pd.read_csv(io.StringIO(file_content.decode('utf-8-sig')))
            df.columns = [c.lower() for c in df.columns]
            
            if 'name' not in df.columns or 'age' not in df.columns:
                return []

            new_users = []
            # 為了效能，我們一次把所有現有名稱撈出來比對
            # (或是依賴 DB 的 Unique Constraint 拋錯也可以，這裡維持原本邏輯)
            existing_names = {u.name for u in db.query(User.name).all()} # Set of names

            for _, row in df.iterrows():
                name = str(row['name'])
                if name not in existing_names:
                    db_user = User(name=name, age=int(row['age']))
                    db.add(db_user)
                    new_users.append({"name": name, "age": int(row['age'])})
                    existing_names.add(name) # 避免 CSV 內部重複
            
            db.commit() # 一次 Commit 所有新資料
            return new_users
        except Exception as e:
            print(f"CSV Process Error: {e}")
            db.rollback() # 發生錯誤要回滾
            return []

    @staticmethod
    def calculate_age_stats(db: Session):
        # 直接用 Pandas 從 SQL 讀取資料！這比自己轉 List 快多了
        # SQL: SELECT * FROM users;
        statement = db.query(User).statement
        df = pd.read_sql(statement, db.bind)
        
        if df.empty:
            return {}

        df['group'] = df['name'].astype(str).str[0]
        result = df.groupby('group')['age'].mean().to_dict()
        return result
    
    @staticmethod
    def export_users_csv(db: Session):
        # 1. 使用 Pandas 直接從 SQL 讀取 DataFrame
        statement = db.query(User).statement
        df = pd.read_sql(statement, db.bind)
        
        # 2. 移除 id 欄位 (通常匯出給使用者看不需要系統 id)
        if 'id' in df.columns:
            df = df.drop(columns=['id'])

        # 3. 轉為 CSV String Buffer
        stream = io.StringIO()
        # index=False 代表不要匯出 Pandas 的索引值 (0, 1, 2...)
        df.to_csv(stream, index=False)
        
        # 4. 指標回到開頭，準備讀取
        stream.seek(0)
        return stream