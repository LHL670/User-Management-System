from pydantic import BaseModel, field_validator

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

class UserResponse(UserCreate):
    pass