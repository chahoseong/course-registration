from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Literal

class UserBase(BaseModel):
    email: str
    name: str
    role: Literal["student", "admin"] = "student"

class UserCreate(UserBase):
    uid: str

class User(UserBase):
    model_config = ConfigDict(from_attributes=True)
    
    uid: str

