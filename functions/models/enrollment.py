from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from typing import List

class EnrollmentBase(BaseModel):
    course_id: str
    student_ids: List[str] = []

class EnrollmentCreate(EnrollmentBase):
    pass

class Enrollment(EnrollmentBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: str  # This will be the course_id to ensure one enrollment doc per course
    timestamp: datetime = Field(default_factory=datetime.now)

