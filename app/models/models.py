from pydantic import BaseModel, field_validator, ConfigDict

class UserCreate(BaseModel):
    name: str
    age: int

    # TC1: User name is empty 
    @field_validator('name')
    def name_must_not_be_empty(cls, v):
        if not v or v.strip() == "":
            raise ValueError('Name cannot be empty')
        return v

    # TC2: User age is 999 
    @field_validator('age')
    def age_must_be_realistic(cls, v):
        if v >= 150: # 假設 150 歲以上為異常
            raise ValueError('Age is not valid')
        return v

class UserUpdate(BaseModel):
    age: int

    # 確保更新的時候，年齡也不能寫 999
    @field_validator('age')
    def age_must_be_realistic(cls, v):
        if v < 0 or v >= 150:
            raise ValueError('Age is not valid')
        return v

class UserResponse(UserCreate):
    #  讓 Pydantic 可以讀取 SQLAlchemy 物件
    model_config = ConfigDict(from_attributes=True)