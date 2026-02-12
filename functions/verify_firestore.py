import os
from google.cloud import firestore

os.environ["FIRESTORE_EMULATOR_HOST"] = "127.0.0.1:8080"
project_id = "course-registration-711a4"

def verify():
    db = firestore.Client(project=project_id)
    
    print("--- Firestore Verification ---")
    
    # Check users
    users = list(db.collection("users").stream())
    print(f"Users found: {len(users)}")
    for user in users:
        print(f" - {user.id}: {user.to_dict()['name']} ({user.to_dict()['role']})")
        
    # Check courses
    courses = list(db.collection("courses").stream())
    print(f"Courses found: {len(courses)}")
    for course in courses:
        print(f" - {course.id}: {course.to_dict()['title']}")

if __name__ == "__main__":
    verify()
