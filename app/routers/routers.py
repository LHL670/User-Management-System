from fastapi import APIRouter, HTTPException, UploadFile, File, status
from typing import List
from ..models.models import UserCreate, UserResponse
from ..services.user_services import UserService

# 建立一個 Router
router = APIRouter()

# 1. Get Users
@router.get("/users", response_model=List[UserResponse], summary="Get user list")
def get_users():
    return UserService.get_all_users()

# 2. Create User
@router.post("/users", status_code=status.HTTP_201_CREATED, summary="Create a user")
def create_user(user: UserCreate):
    created_user = UserService.create_user(user)
    
    # 判斷是否回傳 None (代表重複)
    if created_user is None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, # 409 
            detail=f"User with name '{user.name}' already exists."
        )
        
    return created_user

# 3. Delete User
@router.delete("/users/{name}", summary="Delete user by name")
def delete_user(name: str):
    success = UserService.delete_user_by_name(name)
    if not success:
        raise HTTPException(status_code=404, detail="User not found")
    return {"status": "success", "message": f"User {name} deleted"}

# 4. Batch Upload CSV 
@router.post(
    "/users/upload", 
    summary="Batch add users from CSV",
    description="Upload a CSV file to batch create users."
)
async def upload_users(
    file: UploadFile = File(..., media_type="multipart/form-data")
):
    # 後端雙重驗證：確保即使前端放行，後端也只收 CSV
    if not file.filename.lower().endswith('.csv'):
        raise HTTPException(status_code=400, detail="Invalid file type. Please upload a CSV.")
    
    content = await file.read()
    added_users = await UserService.process_csv_upload(content)
    
    return {"status": "success", "added_count": len(added_users), "data": added_users}

# 5. Statistics
@router.get("/users/stats/age-group", summary="Calculate average age by group")
def get_user_stats():
    return UserService.calculate_age_stats()