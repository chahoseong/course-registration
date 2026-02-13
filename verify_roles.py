
import os
from google.cloud import firestore
import firebase_admin
from firebase_admin import auth, credentials

# Emulators configuration
os.environ["FIRESTORE_EMULATOR_HOST"] = "127.0.0.1:8080"
os.environ["FIREBASE_AUTH_EMULATOR_HOST"] = "127.0.0.1:9099"
project_id = "course-registration-711a4"

def check_users():
    db_id = os.getenv("FIREBASE_DATABASE_ID", "course-registration")
    print(f"Connecting to Firestore DB: {db_id}")
    
    db = firestore.Client(project=project_id, database=db_id)
    
    print("--- Users in Firestore ---")
    users = list(db.collection("users").stream())
    for user in users:
        data = user.to_dict()
        print(f"UID: {user.id}")
        print(f"  Name: {data.get('name')}")
        print(f"  Role: {data.get('role')}")
        print(f"  Email: {data.get('email')}")
        print("-" * 20)

if __name__ == "__main__":
    check_users()
