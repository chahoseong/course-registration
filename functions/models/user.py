from pydantic import BaseModel, ConfigDict
from typing import Literal, Optional

class UserBase(BaseModel):
    email: Optional[str] = None
    displayName: Optional[str] = None
    photoURL: Optional[str] = None
    role: Literal["student", "admin"] = "student"

class UserCreate(UserBase):
    uid: str

class User(UserBase):
    model_config = ConfigDict(from_attributes=True)
    
    uid: str

