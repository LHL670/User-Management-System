import unittest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# 匯入你的 App 與 資料庫設定
from app.main import app
from app.database.database import Base, get_db

# 1. 設定測試用的 SQLite 資料庫 (In-Memory)
# 使用 StaticPool 是關鍵：讓 In-Memory 資料庫在多個連線間保持狀態，直到測試結束
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 2. 定義 Override Dependency
# 這是一個 Generator，用來取代原本 app/database.py 裡的 get_db
def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

# 3. 強制 FastAPI 使用測試資料庫
app.dependency_overrides[get_db] = override_get_db

class TestUserAPI(unittest.TestCase):
    def setUp(self):
        """
        每個測試案例開始前執行
        """
        self.client = TestClient(app)
        # 在測試資料庫中建立所有資料表 (Create Tables)
        Base.metadata.create_all(bind=engine)

    def tearDown(self):
        """
        每個測試案例結束後執行
        """
        # 刪除所有資料表，確保下一個測試是乾淨的 (Drop Tables)
        Base.metadata.drop_all(bind=engine)

    # --- 以下測試邏輯保持不變 (除了不再需要 fake_db.clear) ---

    def test_create_user_success(self):
        response = self.client.post("/users", json={"name": "TestUser", "age": 25})
        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertEqual(data["name"], "TestUser")
        self.assertEqual(data["age"], 25)

    def test_create_duplicate_user(self):
        # 第一次建立
        self.client.post("/users", json={"name": "UniqueUser", "age": 20})
        
        # 第二次建立相同名字
        response = self.client.post("/users", json={"name": "UniqueUser", "age": 30})
        
        # 預期收到 409 Conflict
        self.assertEqual(response.status_code, 409)
        self.assertIn("already exists", response.json()["detail"])

    def test_tc1_create_user_empty_name(self):
        response = self.client.post("/users", json={"name": "", "age": 25})
        self.assertEqual(response.status_code, 422)
        self.assertIn("Name cannot be empty", response.text)

    def test_tc2_create_user_invalid_age(self):
        response = self.client.post("/users", json={"name": "OldMan", "age": 999})
        self.assertEqual(response.status_code, 422)
        self.assertIn("Age is not valid", response.text)

    def test_update_user_success(self):
        # 1. 先建立一個使用者
        self.client.post("/users", json={"name": "UpdateTarget", "age": 20})
        
        # 2. 呼叫 PUT 更新年齡為 30
        response = self.client.put("/users/UpdateTarget", json={"age": 30})
        
        # 3. 驗證回應
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["age"], 30)
        self.assertEqual(response.json()["name"], "UpdateTarget")

    def test_update_user_not_found(self):
        # 更新一個不存在的使用者
        response = self.client.put("/users/Ghost", json={"age": 30})
        self.assertEqual(response.status_code, 404)

    def test_update_user_invalid_age(self):
        # 驗證更新時的防呆機制
        self.client.post("/users", json={"name": "ValidUser", "age": 20})
        response = self.client.put("/users/ValidUser", json={"age": 999})
        self.assertEqual(response.status_code, 422)

if __name__ == '__main__':
    unittest.main()