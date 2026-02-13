import firebase_admin
from firebase_admin import firestore
import os
from google.cloud import firestore as google_firestore

def get_db():
    # Firebase Admin SDK가 초기화되지 않았다면 초기화
    if not firebase_admin._apps:
        firebase_admin.initialize_app()
    
    # 환경 변수에서 데이터베이스 ID 로드 (없으면 기본값 사용)
    db_id = os.getenv("FIREBASE_DATABASE_ID", "(default)")
    print(f"[database] Connecting to Firestore DB: {db_id}")
    
    # Project ID 가져오기
    project_id = os.getenv("GCLOUD_PROJECT") or os.getenv("GOOGLE_CLOUD_PROJECT") or "course-registration-711a4"

    # google.cloud.firestore.Client를 직접 사용하여 특정 데이터베이스에 연결
    # firebase_admin.firestore.client()는 기본적으로 (default) DB를 가져오므로 주의 필요
    if db_id == "(default)":
        return google_firestore.Client(project=project_id)
    return google_firestore.Client(project=project_id, database=db_id)
