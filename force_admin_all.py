
import os
from google.cloud import firestore

os.environ["FIRESTORE_EMULATOR_HOST"] = "127.0.0.1:8080"
project_id = "course-registration-711a4"

def make_admin_all_dbs():
    databases = ["(default)", "course-registration"]
    
    for db_name in databases:
        print(f"\n--- Process DB: {db_name} ---")
        try:
            if db_name == "(default)":
                db = firestore.Client(project=project_id)
            else:
                db = firestore.Client(project=project_id, database=db_name)
                
            users = list(db.collection("users").stream())
            if users:
                for user in users:
                    print(f"Setting Admin - UID: {user.id} ({db_name})")
                    db.collection("users").document(user.id).update({"role": "admin"})
            else:
                print(f"No users in {db_name}")
        except Exception as e:
            print(f"Error checking {db_name}: {e}")

if __name__ == "__main__":
    make_admin_all_dbs()
