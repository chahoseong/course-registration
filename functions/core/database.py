import firebase_admin
from google.cloud import firestore
import os

def get_db():
    if not firebase_admin._apps:
        # 에뮬레이터 환경에서 호스트 설정이 필요한 경우 환경 변수 사용
        firebase_admin.initialize_app()
    
    raw_db_id = os.getenv("FIREBASE_DATABASE_ID")
    if raw_db_id is None:
        db_id = "course-registration"
        print("[database] FIREBASE_DATABASE_ID not set. Using default:", db_id)
    else:
        db_id = raw_db_id.strip()
        print("[database] FIREBASE_DATABASE_ID loaded from env:", db_id)
    
    # Cloud Functions 환경 변수 또는 직접 지정
    project_id = os.getenv("GCLOUD_PROJECT") or os.getenv("GOOGLE_CLOUD_PROJECT") or "course-registration-711a4"

    return firestore.Client(project=project_id, database=db_id)
