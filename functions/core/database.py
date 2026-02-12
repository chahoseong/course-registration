import firebase_admin
from firebase_admin import firestore
import os

def get_db():
    if not firebase_admin._apps:
        # 에뮬레이터 환경에서 호스트 설정이 필요한 경우 환경 변수 사용
        firebase_admin.initialize_app()
    return firestore.client()
