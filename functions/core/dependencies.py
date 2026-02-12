from core.database import get_db
from repositories.firestore_repo import FirestoreCourseRepository, FirestoreEnrollmentRepository, FirestoreUserRepository
from services.course_service import CourseService
from services.enrollment_service import EnrollmentService
from services.user_service import UserService


def get_course_service():
    db = get_db()
    repo = FirestoreCourseRepository(db)
    return CourseService(repo)


def get_enrollment_service():
    db = get_db()
    course_repo = FirestoreCourseRepository(db)
    enroll_repo = FirestoreEnrollmentRepository(db)
    return EnrollmentService(course_repo, enroll_repo)


def get_user_service():
    db = get_db()
    repo = FirestoreUserRepository(db)
    return UserService(repo)


from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from firebase_admin import auth

security = HTTPBearer()


def get_current_user_uid(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    print("[auth] bearer token received for /api request")
    token = credentials.credentials
    try:
        decoded_token = auth.verify_id_token(token)
        print(f"[auth] token verified uid={decoded_token.get('uid')}")
        return decoded_token["uid"]
    except Exception as e:
        print(f"[auth] token verification failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid authentication credentials: {e}",
            headers={"WWW-Authenticate": "Bearer"},
        )


def get_agent_service():
    from services.agent_service import AgentService

    course_service = get_course_service()
    enrollment_service = get_enrollment_service()
    return AgentService(course_service, enrollment_service)
