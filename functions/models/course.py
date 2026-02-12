from pydantic import BaseModel, Field, ConfigDict
from typing import Optional

class CourseBase(BaseModel):
    title: str
    instructor: str
    max_students: int
    current_count: int = 0
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    description: Optional[str] = None

class CourseCreate(CourseBase):
    pass

class Course(CourseBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: str

