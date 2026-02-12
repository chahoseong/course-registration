from firebase_functions import https_fn, options
import firebase_admin
from firebase_admin import initialize_app
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import json

from models.course import Course, CourseCreate
from models.enrollment import Enrollment, EnrollmentCreate
from core.dependencies import get_course_service, get_enrollment_service, get_user_service, get_agent_service
from services.course_service import CourseService
from services.enrollment_service import EnrollmentService, EnrollmentError
from services.user_service import UserService
from services.agent_service import AgentService

# Firebase Admin 초기화 (중복 방지)
if not firebase_admin._apps:
    initialize_app()

# 전역 지역 설정 (서울)
options.set_global_options(region="asia-northeast3")

# FastAPI 앱 생성
app = FastAPI()

# CORS 설정은 Firebase Functions의 on_request(cors=...)에서 처리하므로 주석 처리
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

@app.get("/api/health")
def health_check():
    return {"status": "ok"}

@app.get("/api/courses")
def list_courses(service: CourseService = Depends(get_course_service)):
    return service.get_all_courses()

@app.get("/api/courses/{course_id}")
def get_course(course_id: str, service: CourseService = Depends(get_course_service)):
    course = service.get_course(course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    return course

@app.post("/api/courses")
def create_course(course: CourseCreate, service: CourseService = Depends(get_course_service)):
    return service.create_course(course)

@app.put("/api/courses/{course_id}")
def update_course(course_id: str, course: CourseCreate, service: CourseService = Depends(get_course_service)):
    # Course model object for saving
    existing = service.get_course(course_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Course not found")
    
    updated_course = Course(id=course_id, **course.model_dump())
    return service.create_course(updated_course) # service.create_course actually calls repo.save

@app.delete("/api/courses/{course_id}")
def delete_course(course_id: str, service: CourseService = Depends(get_course_service)):
    success = service.delete_course(course_id)
    if not success:
        raise HTTPException(status_code=404, detail="Course not found")
    return {"status": "success"}

from pydantic import BaseModel

class EnrollmentRequest(BaseModel):
    student_id: str
    course_id: str

@app.post("/api/enrollments")
def enroll_student(req: EnrollmentRequest, service: EnrollmentService = Depends(get_enrollment_service)):
    try:
        return service.enroll_student(req.student_id, req.course_id)
    except EnrollmentError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/users")
def list_users(service: UserService = Depends(get_user_service)):
    return service.get_all_users()

@app.put("/api/users/{uid}/role")
def update_user_role(uid: str, role: str, service: UserService = Depends(get_user_service)):
    user = service.update_user_role(uid, role)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.get("/api/stats")
def get_stats(
    course_service: CourseService = Depends(get_course_service),
    user_service: UserService = Depends(get_user_service)
):
    courses = course_service.get_all_courses()
    users = user_service.get_all_users()
    
    total_courses = len(courses)
    total_students = len([u for u in users if u.role == 'student'])
    total_enrollments = sum(c.current_count for c in courses)
    
    return {
        "total_courses": total_courses,
        "total_students": total_students,
        "total_enrollments": total_enrollments
    }

class ChatRequest(BaseModel):
    message: str

@app.post("/api/agent/chat")
def agent_chat(req: ChatRequest, service: AgentService = Depends(get_agent_service)):
    # 유저 ID는 실제 환경에서는 토큰에서 추출해야 하지만 우선 간단히 처리
    response = service.chat("user", req.message)
    return {"response": response}

@https_fn.on_request(
    cors=options.CorsOptions(
        cors_origins="*",
        cors_methods=["get", "post", "put", "delete", "options"]
    )
)
def fastapi_handler(req: https_fn.Request) -> https_fn.Response:
    try:
        # ASGI scope 구성
        asgi_request = {
            "type": "http",
            "method": req.method,
            "path": req.path,
            "raw_path": req.path.encode(),
            "headers": [(k.lower().encode(), v.encode()) for k, v in req.headers.items()],
            "query_string": req.query_string.encode() if isinstance(req.query_string, str) else (req.query_string or b""),
        }

        async def receive():
            return {"type": "http.request", "body": req.get_data() or b"", "more_body": False}

        response_body, response_headers, response_status = [], [], 200

        async def send(message):
            nonlocal response_body, response_headers, response_status
            if message["type"] == "http.response.start":
                response_status = message.get("status", 200)
                response_headers = message.get("headers", [])
            elif message["type"] == "http.response.body":
                response_body.append(message.get("body", b""))

        async def run_asgi():
            await app(asgi_request, receive, send)

        asyncio.run(run_asgi())

        full_body = b"".join(response_body)
        headers_dict = {
            k.decode() if isinstance(k, bytes) else k: v.decode() if isinstance(v, bytes) else v
            for k, v in response_headers
        }

        return https_fn.Response(response=full_body, status=response_status, headers=headers_dict)

    except Exception as e:
        return https_fn.Response(
            response=json.dumps({"error": f"Internal Server Error: {str(e)}"}),
            status=500,
            headers={"Content-Type": "application/json"},
        )