import pandas as pd
import io
from ..models.models import UserCreate

# 模擬資料庫
fake_db = []

class UserService:
    @staticmethod
    def get_all_users():
        return fake_db

    @staticmethod
    def create_user(user: UserCreate):
        # 檢查是否已經有這個名字
        if any(u['name'] == user.name for u in fake_db):
            return None  # 回傳 None 代表建立失敗 (已存在)

        user_data = user.model_dump()
        fake_db.append(user_data)
        return user_data

    @staticmethod
    def delete_user_by_name(name: str) -> bool:
        global fake_db
        initial_count = len(fake_db)
        fake_db = [u for u in fake_db if u["name"] != name]
        return len(fake_db) < initial_count

    @staticmethod
    async def process_csv_upload(file_content: bytes) -> list[dict]:
        try:
            df = pd.read_csv(io.StringIO(file_content.decode('utf-8-sig')))
            
            df.columns = [c.lower() for c in df.columns]
            
            if 'name' not in df.columns or 'age' not in df.columns:
                print(f"Error: Missing columns. Found {df.columns}")
                return []

            new_users = []
            existing_names = {u['name'] for u in fake_db}

            for _, row in df.iterrows():
                name = str(row['name'])
                # 只有當名字不在 existing_names 裡面時才新增
                if name not in existing_names:
                    user = {"name": name, "age": int(row['age'])}
                    fake_db.append(user)
                    new_users.append(user)
                    existing_names.add(name)
                
            return new_users
        except Exception as e:
            print(f"CSV Process Error: {e}")
            return []

    @staticmethod
    def calculate_age_stats():
        if not fake_db:
            return {}
        
        df = pd.DataFrame(fake_db)
        if 'name' not in df.columns or 'age' not in df.columns:
            return {}

        # 依照名字首字元分組計算平均年齡
        df['group'] = df['name'].astype(str).str[0]
        result = df.groupby('group')['age'].mean().to_dict()
        return result