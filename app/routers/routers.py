from fastapi import APIRouter, HTTPException, UploadFile, File, status, Depends
from fastapi.responses import StreamingResponse # 用於下載檔案
from fastapi.security import OAuth2PasswordRequestForm # 用於接收登入表單
from datetime import datetime, timedelta
from typing import List
from sqlalchemy.orm import Session
from ..database.database import get_db
from ..models.models import UserCreate, UserResponse, UserUpdate
from ..services.user_services import UserService
from ..JWT.auth import Token, create_access_token, verify_password, fake_users_db, get_current_user
# 建立一個 Router
router = APIRouter()

@router.post("/token", response_model=Token, summary="Login to get JWT")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    # 驗證帳號密碼
    user = fake_users_db.get(form_data.username)
    if not user or not verify_password(form_data.password, user['hashed_password']):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 產生 Token
    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data={"sub": user["username"]}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

# 1. Get Users
@router.get("/users", response_model=List[UserResponse], summary="Get user list")
def get_users(db: Session = Depends(get_db)):
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

# 3. Delete User (敏感操作 -> 需要登入!)
# 加入 current_user: dict = Depends(get_current_user) 就會強制檢查 Token
@router.delete("/users/{name}", summary="Delete user by name (Protected)")
def delete_user(
    name: str, 
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user) # [新增] 保護鎖
):
    success = UserService.delete_user_by_name(db, name)
    if not success:
        raise HTTPException(status_code=404, detail="User not found")
    return {"status": "success", "message": f"User {name} deleted by {current_user['username']}"}

# 4. Batch Upload CSV (敏感操作 -> 需要登入!)
@router.post("/users/upload", summary="Batch add users from CSV (Protected)")
async def upload_users(
    file: UploadFile = File(...), 
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user) # [新增] 保護鎖
):
    if not file.filename.lower().endswith('.csv'):
        raise HTTPException(status_code=400, detail="Invalid file type.")
    
    content = await file.read()
    added_users = await UserService.process_csv_upload(db, content)
    return {"status": "success", "added_count": len(added_users), "data": added_users}

# [新增] 5. Export CSV (匯出功能)
@router.get("/users/export", summary="Export users to CSV")
def export_users(db: Session = Depends(get_db)):
    # 取得 CSV 串流
    csv_stream = UserService.export_users_csv(db)
    
    # 回傳檔案下載 Response
    return StreamingResponse(
        iter([csv_stream.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=users_export.csv"}
    )

# 5. Statistics
@router.get("/users/stats/age-group")
def get_user_stats(db: Session = Depends(get_db)): 
    return UserService.calculate_age_stats(db)