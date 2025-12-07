from fastapi import APIRouter, HTTPException, UploadFile, File, status, Depends
from typing import List
from sqlalchemy.orm import Session
from ..database.database import get_db
from ..models.models import UserCreate, UserResponse, UserUpdate
from ..services.user_services import UserService

# 建立一個 Router
router = APIRouter()

# 1. Get Users
@router.get("/users", response_model=List[UserResponse], summary="Get user list")
def get_users(db: Session = Depends(get_db)): # [修改] 注入 db
    return UserService.get_all_users(db)

# 2. Create User
@router.post("/users", status_code=status.HTTP_201_CREATED, summary="Create a user")
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    created_user = UserService.create_user(db, user)
    
    # 判斷是否回傳 None (代表重複)
    if created_user is None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, # 409 
            detail=f"User with name '{user.name}' already exists."
        )
        
    return created_user

@router.put("/users/{name}", response_model=UserResponse, summary="Update user age")
def update_user(name: str, user_update: UserUpdate, db: Session = Depends(get_db)): # [修改]
    """
    Update a user's information (specifically age).
    """
    updated_user = UserService.update_user(db, name, user_update)
    
    if updated_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User '{name}' not found"
        )
        
    return updated_user

# 3. Delete User
@router.delete("/users/{name}", summary="Delete user by name")
def delete_user(name: str, db: Session = Depends(get_db)): 
    success = UserService.delete_user_by_name(db, name)
    if not success:
        raise HTTPException(status_code=404, detail="User not found")
    return {"status": "success", "message": f"User {name} deleted"}

# 4. Batch Upload CSV 
@router.post("/users/upload", summary="Batch add users from CSV")
async def upload_users(
    file: UploadFile = File(...), 
    db: Session = Depends(get_db) 
):
    if not file.filename.lower().endswith('.csv'):
        raise HTTPException(status_code=400, detail="Invalid file type.")
    
    content = await file.read()
    added_users = await UserService.process_csv_upload(db, content)
    return {"status": "success", "added_count": len(added_users), "data": added_users}

# 5. Statistics
@router.get("/users/stats/age-group")
def get_user_stats(db: Session = Depends(get_db)): 
    return UserService.calculate_age_stats(db)