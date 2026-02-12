from firebase_functions import https_fn, options
import firebase_admin
from firebase_admin import initialize_app
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import json
import traceback
import os
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

from models.course import Course, CourseCreate
from models.enrollment import Enrollment, EnrollmentCreate
from core.dependencies import get_course_service, get_enrollment_service, get_user_service, get_agent_service, get_current_user_uid
from services.course_service import CourseService
from services.enrollment_service import EnrollmentService, EnrollmentError
from services.user_service import UserService

# Firebase Admin 초기화 (중복 방지)
if not firebase_admin._apps:
    initialize_app()

# 지역 지정 설정 (서울)
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
    try:
        return service.get_all_courses()
    except Exception as e:
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

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

@app.get("/api/enrollments/my")
def get_my_enrollments(uid: str = Depends(get_current_user_uid), service: EnrollmentService = Depends(get_enrollment_service), course_service: CourseService = Depends(get_course_service)):
    """
    학생의 수강 신청 목록을 조회합니다.
    주의: Enrollment 모델 변경(course_id당 하나의 문서, student_ids 리스트)으로 인해,
    반환 값은 '내가 신청한 Enrollment' 객체들의 리스트입니다.
    프론트엔드에서 수강 내역을 보여주려면, Course 상세 정보가 필요할 수 있으므로
    여기서 Course 정보를 포함해서 내려주는 것이 좋습니다.
    """
    enrollments = service.get_student_enrollments(uid)
    
    # 단순히 Enrollment 리스트만 주면, 프론트엔드가 'student_ids'가 포함된 객체를 받게 되어 혼란스러울 수 있음.
    # 기존 프론트엔드 호환성을 위해, '내가 신청한 건'에 대한 정보를 가공해서 줄 수 있음.
    # 하지만 여기서는 일단 Enrollment 객체 자체를 리턴하거나, 
    # Course 정보를 포함한 확장된 응답을 주는 것이 좋음.
    
    # 확장된 응답: [ { enrollment_id, course: { ... }, timestamp }, ... ]
    result = []
    for enroll in enrollments:
        course = course_service.get_course(enroll.course_id)
        if course:
            result.append({
                "id": enroll.id,
                "course_id": enroll.course_id,
                "student_id": uid, # 개인화된 응답
                "course": course.model_dump(),
                "timestamp": enroll.timestamp
            })
    return result

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
    try:
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
    except Exception as e:
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

class ChatRequest(BaseModel):
    message: str

@app.post("/api/agent/chat")
def agent_chat(req: ChatRequest, uid: str = Depends(get_current_user_uid), service = Depends(get_agent_service)):
    # Debug: 요청 도달/인증 통과 여부 확인
    print(f"[agent_chat] request received uid={uid} message={req.message}")
    try:
        response = service.chat(uid, req.message)
        print(f"[agent_chat] response generated uid={uid}")
        return {"response": response}
    except Exception as e:
        print(f"[agent_chat] error uid={uid}: {e}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Agent processing error: {str(e)}")

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
