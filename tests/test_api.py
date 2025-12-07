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
        # 驗證更新時的防呆機制 (Bonus TC2 也要適用於更新)
        self.client.post("/users", json={"name": "ValidUser", "age": 20})
        response = self.client.put("/users/ValidUser", json={"age": 999})
        self.assertEqual(response.status_code, 422)

if __name__ == '__main__':
    unittest.main()