from core.database import get_db
from repositories.firestore_repo import FirestoreCourseRepository, FirestoreEnrollmentRepository, FirestoreUserRepository
from services.course_service import CourseService
from services.enrollment_service import EnrollmentService

def get_course_service():
    db = get_db()
    repo = FirestoreCourseRepository(db)
    return CourseService(repo)

def get_enrollment_service():
    db = get_db()
    course_repo = FirestoreCourseRepository(db)
    enroll_repo = FirestoreEnrollmentRepository(db)
    return EnrollmentService(course_repo, enroll_repo)
