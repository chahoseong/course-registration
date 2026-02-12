from pydantic import BaseModel, ConfigDict
from datetime import datetime

class EnrollmentBase(BaseModel):
    student_id: str
    course_id: str

class EnrollmentCreate(EnrollmentBase):
    pass

class Enrollment(EnrollmentBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: str  # studentId_courseId
    timestamp: datetime

