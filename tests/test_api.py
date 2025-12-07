import unittest
from fastapi.testclient import TestClient
from app.main import app
from app.services.user_services import fake_db

class TestUserAPI(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        fake_db.clear() # 清空 In-Memory DB

    def test_create_user_success(self):
        response = self.client.post("/users", json={"name": "TestUser", "age": 25})
        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertEqual(data["name"], "TestUser")
        self.assertEqual(data["age"], 25)

    def test_create_duplicate_user(self):
        # 測試重複建立使用者 (驗證 409 Conflict)
        # 第一次建立
        self.client.post("/users", json={"name": "UniqueUser", "age": 20})
        
        # 第二次建立相同名字
        response = self.client.post("/users", json={"name": "UniqueUser", "age": 30})
        
        # 預期收到 409 Conflict
        self.assertEqual(response.status_code, 409)
        self.assertIn("already exists", response.json()["detail"])

    def test_tc1_create_user_empty_name(self):
        # 422 Unprocessable Entity (由 Pydantic 攔截)
        response = self.client.post("/users", json={"name": "", "age": 25})
        self.assertEqual(response.status_code, 422)
        # 檢查錯誤訊息是否包含在 Model 定義的內容
        self.assertIn("Name cannot be empty", response.text)

    def test_tc2_create_user_invalid_age(self):
        response = self.client.post("/users", json={"name": "OldMan", "age": 999})
        self.assertEqual(response.status_code, 422)
        self.assertIn("Age is not valid", response.text)

if __name__ == '__main__':
    unittest.main()