import os
from google.cloud import firestore

# 에뮬레이터 환경 설정
os.environ["FIRESTORE_EMULATOR_HOST"] = "127.0.0.1:8080"
project_id = "course-registration-711a4"

def seed_data():
    # 환경 변수 또는 직접 지정한 데이터베이스 ID 사용
    db_id = os.getenv("FIREBASE_DATABASE_ID", "course-registration")
    db = firestore.Client(project=project_id, database=db_id)

    print("Seeding users...")
    users = {
        "admin_uid_123": {"name": "관리자", "role": "admin", "email": "admin@example.com"},
        "student_uid_456": {"name": "홍길동", "role": "student", "email": "hong@example.com"},
        "student_uid_789": {"name": "김철수", "role": "student", "email": "kim@example.com"},
    }
    
    for uid, data in users.items():
        db.collection("users").document(uid).set(data)
        print(f"Added user: {uid}")

    print("Seeding courses...")
    courses = [
        {"title": "AI 에이전트 입문", "instructor": "이박사", "max_students": 30, "current_count": 0},
        {"title": "React 프론트엔드 실습", "instructor": "최교수", "max_students": 25, "current_count": 0},
        {"title": "Firebase 서버리스 구축", "instructor": "박엔지니어", "max_students": 20, "current_count": 0},
    ]
    
    for course in courses:
        doc_ref = db.collection("courses").document()
        doc_ref.set(course)
        print(f"Added course: {course['title']} (ID: {doc_ref.id})")

    print("Seeding completed successfully!")

if __name__ == "__main__":
    seed_data()
